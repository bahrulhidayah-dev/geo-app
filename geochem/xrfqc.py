# geochem/xrfqc.py
# Optional XRF quality-control module, based on
#   Mikuni K., Ishikawa A. and Sato R. (2025) Accurate determination of
#   whole-rock major element composition of ultramafic rocks through X-ray
#   fluorescence spectrometry. Geochemical Journal 59(6), 299-314.
#   doi:10.2343/geochemj.GJ25017 (CC BY 4.0)
# Three tools:
#   1. reference library of the paper's Table 1;
#   2. QC of reference materials measured with the samples
#      (measured vs reference, deviation, accuracy of their Eq. 7);
#   3. ultramafic check: T-Fe2O3 measured by XRF without Ca-Mg matrix
#      correction is ~0.6-0.7 wt% too high in peridotites, which lowers Mg#.
# Part of GeoChem App (GPL-3.0).

import re
from pathlib import Path

import numpy as np
import pandas as pd

from . import calc
from .plotting import STYLES, _APP, _figure, _style_axes

CITATION = ("Mikuni K., Ishikawa A. and Sato R. (2025) Accurate determination of "
            "whole-rock major element composition of ultramafic rocks through X-ray "
            "fluorescence spectrometry. Geochemical Journal 59(6), 299-314. "
            "doi:10.2343/geochemj.GJ25017")
DOI_URL = "https://doi.org/10.2343/geochemj.GJ25017"

COMPONENTS = ["SiO2", "TiO2", "Al2O3", "Fe2O3t", "MnO", "MgO", "CaO", "Na2O",
              "K2O", "P2O5", "Cr", "Ni"]
UNITS = {c: "wt%" for c in COMPONENTS} | {"Cr": "ug/g", "Ni": "ug/g"}
LABELS = {"Fe2O3t": "T-Fe2O3"}

# Element fraction in the oxide (for Cr2O3 or NiO columns given in wt%)
CR_PER_CR2O3 = 2 * 51.996 / 151.990
NI_PER_NIO = 58.693 / 74.692

# T-Fe2O3 excess (wt%) in peridotitic RMs without matrix correction
# (Mikuni et al. 2025, Fig. 2b and text: JP-1 0.64-0.66, JP-2 0.67-0.74,
# UB-N 0.69-0.72 wt%). Used only for a sensitivity check, never as a correction.
FE_EXCESS_LOW, FE_EXCESS_HIGH = 0.6, 0.7


def load_library():
    lib = pd.read_csv(Path(__file__).parent / "reference_materials.csv", comment="#")
    return lib.set_index("RM")


def rm_key(name):
    """'JB-1a' -> 'JB1A', 'jp 1' -> 'JP1'."""
    return re.sub(r"[\s_\-.#/]", "", str(name)).upper()


def detect(df, library):
    """Find rows whose text cells name a reference material.
    A cell matches when the whole cell, or its first word before a space,
    underscore, '#' or '(' is the RM name (dashes optional): 'JB-1a',
    'JB1a', 'JP-1 run2' and 'JP-1_bead2' all match."""
    keys = {rm_key(r): r for r in library.index}
    found = pd.Series(pd.NA, index=df.index, dtype=object)
    text_cols = df.select_dtypes(exclude="number").columns
    for col in text_cols:
        for i, v in df[col].items():
            if pd.notna(found[i]) or pd.isna(v):
                continue
            s = str(v).strip()
            first = re.split(r"[\s_#(]", s, maxsplit=1)[0]
            for cand in (s, first):
                k = rm_key(cand)
                if k in keys:
                    found[i] = keys[k]
                    break
    return found


def measured(df):
    """The QC components from a sample table (missing ones are left out)."""
    out = {}
    for c in COMPONENTS:
        if c == "Fe2O3t":
            if "Fe2O3t" in df:
                out[c] = df["Fe2O3t"]
            else:
                fe = calc.feot(df)
                if fe.notna().any():
                    out[c] = fe / calc.FEO_PER_FE2O3
        elif c == "Cr":
            if "Cr" in df:
                out[c] = df["Cr"]
            elif "Cr2O3" in df:
                out[c] = df["Cr2O3"] * CR_PER_CR2O3 * 1e4
        elif c == "Ni":
            if "Ni" in df:
                out[c] = df["Ni"]
            elif "NiO" in df:
                out[c] = df["NiO"] * NI_PER_NIO * 1e4
        elif c in df:
            out[c] = df[c]
    return pd.DataFrame(out, index=df.index)


def qc_table(df, rm, library, names, rel_tol=5.0):
    """Long table: one row per measured RM x component.
    Flag 'outside' when |difference| > max(rel_tol % of the reference value,
    an absolute floor of 0.02 wt% or 5 ug/g) - the floor stops trace-level
    oxides (e.g. P2O5 in a dunite) from failing on tiny absolute differences."""
    meas = measured(df)
    rows = []
    for i in rm.dropna().index:
        r = rm[i]
        for c in meas.columns:
            m = meas.at[i, c]
            ref = library.at[r, c]
            if pd.isna(m) or pd.isna(ref):
                continue
            diff = m - ref
            floor = 5.0 if UNITS[c] == "ug/g" else 0.02
            tol = max(abs(ref) * rel_tol / 100, floor)
            rows.append({"Sample": names[i], "RM": r, "Component": LABELS.get(c, c),
                         "key": c, "Unit": UNITS[c], "Measured": m, "Reference": ref,
                         "Difference": diff,
                         "Deviation (%)": 100 * diff / ref if ref else np.nan,
                         "Status": "outside" if abs(diff) > tol else "ok"})
    return pd.DataFrame(rows)


def accuracy(table):
    """Accuracy per component, Mikuni et al. (2025) Eq. 7:
    sqrt( sum (C_measured - C_reference)^2 / (n - 1) ), n = number of RM
    measurements (needs n >= 2)."""
    out = []
    for c in COMPONENTS:
        part = table[table["key"] == c]
        n = len(part)
        if n == 0:
            continue
        acc = np.sqrt((part["Difference"] ** 2).sum() / (n - 1)) if n >= 2 else np.nan
        out.append({"Component": LABELS.get(c, c), "Unit": UNITS[c], "n": n,
                    "Accuracy (Eq. 7)": acc,
                    "Mean difference": part["Difference"].mean(),
                    "Outside tolerance": int((part["Status"] == "outside").sum())})
    return pd.DataFrame(out)


def _mg_number(mgo, fe2o3t):
    mg = mgo / calc.MW["MgO"]
    fe = calc.FEO_PER_FE2O3 * fe2o3t / calc.MW["FeO"]
    return 100 * mg / (mg + fe)


def ultramafic_check(df, names, mgo_min=30.0):
    """Samples with MgO >= mgo_min: Mg# as reported and if T-Fe2O3 were
    0.6-0.7 wt% lower (the bias of uncorrected XRF in peridotites).
    This is a sensitivity estimate, not a correction."""
    if "MgO" not in df:
        return None
    fe = measured(df).get("Fe2O3t")
    if fe is None:
        return None
    sel = df["MgO"] >= mgo_min
    if not sel.any():
        return pd.DataFrame()
    mgo, f = df.loc[sel, "MgO"], fe[sel]
    mg0 = _mg_number(mgo, f)
    mg_lo = _mg_number(mgo, f - FE_EXCESS_LOW)
    mg_hi = _mg_number(mgo, f - FE_EXCESS_HIGH)
    return pd.DataFrame({
        "Sample": names[sel], "MgO": mgo, "T-Fe2O3": f,
        "Mg# (as reported)": mg0,
        f"Mg# if T-Fe2O3 -{FE_EXCESS_LOW}": mg_lo,
        f"Mg# if T-Fe2O3 -{FE_EXCESS_HIGH}": mg_hi,
        "Possible shift in Mg#": mg_hi - mg0,
    })


# Distinct colours (Okabe-Ito based, then extra) for reference materials
RM_COLOURS = ["#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00",
              "#CC79A7", "#999999", "#7FC97F", "#BEAED4", "#FDC086", "#386CB0"]


def rm_colours(rms):
    return {r: RM_COLOURS[i % len(RM_COLOURS)] for i, r in enumerate(rms)}


def plot_deviation(table, style="dark", rel_tol=5.0):
    """Relative deviation (%) of every comparison, one column per component.
    Easier to read than the 1:1 panels when values are close."""
    s = STYLES[style]
    comps = [c for c in COMPONENTS if c in set(table["key"])]
    fig = _figure((max(6.0, 0.62 * len(comps) + 2.2), 3.6))
    fig.patch.set_facecolor(s["bg"])
    ax = fig.subplots()
    ax.axhspan(-rel_tol, rel_tol, color=s["field"], alpha=0.15, linewidth=0, zorder=1)
    ax.axhline(0, color=s["line"], lw=float(_APP["line_width"]), zorder=2)
    rms = list(dict.fromkeys(table["RM"]))
    colour = rm_colours(rms)
    nr = len(rms)
    for j, r in enumerate(rms):
        part = table[table["RM"] == r]
        x = [comps.index(c) + (j - (nr - 1) / 2) * min(0.08, 0.7 / max(nr, 1))
             for c in part["key"]]
        ax.scatter(x, part["Deviation (%)"], s=30, color=colour[r], edgecolor=s["edge"],
                   linewidth=float(_APP["marker_edge"]), zorder=4, label=r)
        bad = (part["Status"] == "outside").values
        if bad.any():
            ax.scatter(np.array(x)[bad], part["Deviation (%)"].values[bad], s=110,
                       facecolor="none", edgecolor="#E05252", linewidth=1.3, zorder=5)
    ax.set_xticks(range(len(comps)))
    ax.set_xticklabels([LABELS.get(c, c) for c in comps])
    lim = np.nanmax(np.abs(table["Deviation (%)"].clip(-100, 100)))
    lim = max(lim * 1.15, rel_tol * 2)
    ax.set_ylim(-lim, lim)
    ax.set_xlim(-0.6, len(comps) - 0.4)
    ax.grid(axis="y", color=s["grid"], lw=0.6, zorder=0)
    _style_axes(ax, s, None, "Deviation from reference (%)")
    leg = ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1), frameon=False,
                    fontsize=_APP["font_legend"])
    for txt in leg.get_texts():
        txt.set_color(s["fg"])
    fig.tight_layout()
    return fig


def plot_qc(table, style="dark", rel_tol=5.0, ncol=4):
    """Measured vs reference for each component: 1:1 line and a
    tolerance band; one colour per reference material."""
    s = STYLES[style]
    comps = [c for c in COMPONENTS if c in set(table["key"])]
    n = len(comps)
    ncol = min(ncol, n)
    nrow = int(np.ceil(n / ncol))
    fig = _figure((2.75 * ncol, 2.55 * nrow + 0.5))
    fig.patch.set_facecolor(s["bg"])
    axes = np.atleast_1d(fig.subplots(nrow, ncol)).ravel()
    rms = list(dict.fromkeys(table["RM"]))
    colour = rm_colours(rms)
    for ax, c in zip(axes, comps):
        part = table[table["key"] == c]
        lo = min(part["Reference"].min(), part["Measured"].min())
        hi = max(part["Reference"].max(), part["Measured"].max())
        pad = (hi - lo) * 0.08 or max(abs(hi) * 0.1, 0.01)
        a, b = max(lo - pad, 0), hi + pad
        xx = np.linspace(a, b, 50)
        floor = 5.0 if UNITS[c] == "ug/g" else 0.02
        band = np.maximum(xx * rel_tol / 100, floor)
        ax.fill_between(xx, xx - band, xx + band, color=s["field"], alpha=0.15,
                        linewidth=0, zorder=1)
        ax.plot([a, b], [a, b], color=s["line"], lw=float(_APP["line_width"]), zorder=2)
        for r, p in part.groupby("RM", sort=False):
            bad = p["Status"] == "outside"
            ax.scatter(p["Reference"], p["Measured"], s=34, color=colour[r],
                       edgecolor=s["edge"], linewidth=float(_APP["marker_edge"]),
                       zorder=4, label=r)
            if bad.any():
                ax.scatter(p.loc[bad, "Reference"], p.loc[bad, "Measured"], s=120,
                           facecolor="none", edgecolor="#E05252", linewidth=1.3, zorder=5)
        ax.set_xlim(a, b)
        ax.set_ylim(a, b)
        ax.set_aspect("equal", adjustable="box")
        _style_axes(ax, s, f"Reference ({UNITS[c]})", f"Measured ({UNITS[c]})")
        ax.set_title(LABELS.get(c, c), color=s["fg"], fontsize=_APP["font_axis"] + 1,
                     family=_APP["font_family"], fontweight="bold")
    for ax in axes[n:]:
        ax.set_visible(False)
    seen = {}
    for ax in axes[:n]:
        for h, l in zip(*ax.get_legend_handles_labels()):
            seen.setdefault(l, h)
    leg = fig.legend(list(seen.values()), list(seen.keys()), loc="lower center",
                     ncol=min(len(seen), 8), frameon=False,
                     fontsize=_APP["font_legend"])
    for txt in leg.get_texts():
        txt.set_color(s["fg"])
    fig.tight_layout(rect=(0, 0.06 if nrow > 1 else 0.1, 1, 1))
    return fig
