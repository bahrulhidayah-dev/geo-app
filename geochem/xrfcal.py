# geochem/xrfcal.py
# XRF calibration from raw X-ray intensities (fused glass beads), with an
# optional matrix correction, after
#   Mikuni K., Ishikawa A. and Sato R. (2025) Geochemical Journal 59(6),
#   299-314. doi:10.2343/geochemj.GJ25017 (CC BY 4.0)
#
# Equations (numbers as in the paper):
#   (8)  Y_i = (1/DF) * C_i,ref * Total_wet / Total_dry
#        reference value in the glass bead. Total_dry = sum of the oxides in
#        the as-received (wet) sample, Total_wet = Total_dry + LOI.
#   (1)  X_i = a * I_i + b                     calibration line (bead wt%)
#   (4)  I_i,corr = I_i * (1 + sum_j A_j W_j)  matrix correction; W_j = bead
#        concentration of a coexisting element j. A_j come from a multiple
#        regression on the calibration standards.
#   (5)  X'_i = a' * I_i,corr + b'
#   (6)  R^2 on the bead concentrations
#   (7)  accuracy = sqrt( sum (C_calc - C_ref)^2 / (n - 1) ), wet sample
# Validated against the paper (Tables 3-5): T-Fe2O3 with Ca-Mg correction
# gives A_Ca = 0.069, A_Mg = -0.011, R^2 = 0.99967, accuracy = 0.077 wt%,
# and GP13 8.92 -> 8.40 wt% T-Fe2O3.
# Part of GeoChem App (GPL-3.0).

import re
from pathlib import Path

import numpy as np
import pandas as pd

from .plotting import STYLES, _APP, _figure, _style_axes

OXIDES = ["SiO2", "TiO2", "Al2O3", "Fe2O3t", "MnO", "MgO", "CaO", "Na2O", "K2O",
          "P2O5", "Cr2O3", "NiO"]
LABELS = {"Fe2O3t": "T-Fe2O3"}
ELEMENT = {"Si": "SiO2", "Ti": "TiO2", "Al": "Al2O3", "Fe": "Fe2O3t", "Mn": "MnO",
           "Mg": "MgO", "Ca": "CaO", "Na": "Na2O", "K": "K2O", "P": "P2O5",
           "Cr": "Cr2O3", "Ni": "NiO"}
CR2O3_PER_CR = 151.990 / (2 * 51.996)
NIO_PER_NI = 74.692 / 58.693
MAX_FACTOR = 0.1     # the paper excludes correction factors with |A| > 0.1
EXAMPLE_FILE = Path(__file__).parent / "xrf_example_mikuni2025.csv"


def label(ox):
    return LABELS.get(ox, ox)


# ---------------- reading the intensity table ----------------
def _k(name):
    s = str(name).strip().lower()
    s = re.sub(r"\(.*?\)|\[.*?\]", "", s)
    s = s.replace("α", "a")
    s = re.sub(r"[\s_\-.]", "", s)
    s = re.sub(r"(kcps|cps|intensity|int)$", "", s)
    s = re.sub(r"(ka|ka1|kalpha)$", "", s)
    return s


def find_columns(df):
    """Map intensity columns to oxides and find the DF and LOI columns.
    Accepts 'Si', 'Si Ka', 'Si Kα', 'SiO2', 'Fe', 'T-Fe2O3', 'Fe2O3t', ...
    Returns ({oxide: column}, df_column or None, loi_column or None)."""
    keys = {}
    for el, ox in ELEMENT.items():
        keys[el.lower()] = ox
        keys[ox.lower()] = ox
    keys.update({"tfe2o3": "Fe2O3t", "fe2o3": "Fe2O3t", "fe2o3total": "Fe2O3t",
                 "feo": "Fe2O3t", "cr2o3": "Cr2O3", "nio": "NiO"})
    found, df_col, loi_col = {}, None, None
    for c in df.columns:
        k = _k(c)
        if k in ("df", "dilution", "dilutionfactor", "dil"):
            df_col = df_col or c
        elif k in ("loi", "lossonignition"):
            loi_col = loi_col or c
        elif k in keys and keys[k] not in found and pd.api.types.is_numeric_dtype(df[c]):
            found[keys[k]] = c
    return {ox: found[ox] for ox in OXIDES if ox in found}, df_col, loi_col


def rm_key(name):
    return re.sub(r"[\s_\-.#/]", "", str(name)).upper()


def standards(names, library):
    """RM name for rows whose whole sample name is a reference material
    ('JB-1a', 'JB1a'); rows like 'JB-3-1' or 'JP-2#2' are left out
    (drift checks and working standards are measured as unknowns)."""
    keys = {rm_key(r): r for r in library.index}
    return pd.Series([keys.get(rm_key(n), pd.NA) for n in names], index=names.index,
                     dtype=object)


# ---------------- reference values ----------------
def reference_wet(library):
    """Reference values (wet sample, wt% oxides incl. Cr2O3 and NiO)."""
    ref = library[[o for o in OXIDES if o in library.columns]].copy()
    ref["Cr2O3"] = library["Cr"] * CR2O3_PER_CR * 1e-4
    ref["NiO"] = library["Ni"] * NIO_PER_NI * 1e-4
    return ref[OXIDES]


def bead_reference(ref_wet, dil, loi):
    """Eq. 8: reference concentration in the glass bead, and the factor
    Total_wet / Total_dry used for each standard."""
    total_dry = ref_wet.sum(axis=1)
    factor = (total_dry + loi) / total_dry
    return ref_wet.mul(factor / dil, axis=0), factor


# ---------------- regression ----------------
def _r2(y, yc):
    ss = ((y - y.mean()) ** 2).sum()
    return 1 - ((yc - y) ** 2).sum() / ss if ss > 0 else np.nan


def fit_line(i, y):
    """Eq. 1: y = a i + b (least squares)."""
    a, b = np.polyfit(i, y, 1)
    return {"a": a, "b": b, "A": {}}


def fit_corrected(i, y, w):
    """Eqs. 4-5: y = a' i (1 + sum A_j W_j) + b'.
    Linear form y = a' i + sum (a' A_j) i W_j + b', solved by least squares.
    w: DataFrame of bead concentrations of the correcting elements."""
    cols = list(w.columns)
    m = np.column_stack([i] + [i * w[c].values for c in cols] + [np.ones_like(i)])
    coef, *_ = np.linalg.lstsq(m, y, rcond=None)
    a = coef[0]
    return {"a": a, "b": coef[-1], "A": {c: coef[k + 1] / a for k, c in enumerate(cols)}}


def predict(p, i, w=None):
    corr = 1.0
    if p["A"]:
        corr = 1 + sum(p["A"][c] * np.asarray(w[c], dtype=float) for c in p["A"])
    return p["a"] * np.asarray(i, dtype=float) * corr + p["b"]


# ---------------- the whole calibration ----------------
def calibrate(table, cols, df_col, loi_col, std_rm, library, corrections=None):
    """Build calibration lines from the standards in `table`.
    std_rm: Series (same index as table) with the RM name of each calibration
            standard, NA for the other rows.
    corrections: {oxide: [correcting oxides]}, e.g. {"Fe2O3t": ["CaO", "MgO"]}.
    Returns a dict with the fitted lines and a per-oxide summary."""
    corrections = corrections or {}
    idx = std_rm.dropna().index
    rms = std_rm[idx]
    ref = reference_wet(library).loc[rms.values]
    ref.index = idx
    dil = table.loc[idx, df_col].astype(float)
    loi = (table.loc[idx, loi_col].astype(float) if loi_col else
           pd.Series(np.nan, index=idx))
    loi_used = loi.fillna(library.loc[rms.values, "LOI"].set_axis(idx))
    y_bead, factor = bead_reference(ref, dil, loi_used)
    lines, plain, rows = {}, {}, []
    for ox, c in cols.items():
        ok = table.loc[idx, c].notna() & y_bead[ox].notna()
        if ok.sum() < 3:
            continue
        i = table.loc[idx[ok], c].astype(float).values
        y = y_bead.loc[ok, ox].values
        p0 = fit_line(i, y)
        plain[ox] = p0
        use = [w for w in corrections.get(ox, []) if w in y_bead and w != ox]
        p = fit_corrected(i, y, y_bead.loc[ok, use]) if use else p0
        lines[ox] = p
        for tag, q in (("plain", p0), ("final", p)):
            yc = predict(q, i, y_bead.loc[ok, use] if q["A"] else None)
            wet_calc = yc * dil[ok].values / factor[ok].values
            dev = wet_calc - ref.loc[ok, ox].values
            q["r2"] = _r2(y, yc)
            q["accuracy"] = np.sqrt((dev ** 2).sum() / (len(dev) - 1))
            q["n"] = int(ok.sum())
            q["deviation"] = pd.Series(dev, index=idx[ok])
            q["bead_calc"] = pd.Series(yc, index=idx[ok])
        rows.append({"Component": label(ox), "n": p["n"], "a": p["a"], "b": p["b"],
                     "R2": p["r2"], "Accuracy (wt%)": p["accuracy"],
                     "Matrix correction": ", ".join(f"{label(k)} {v:+.4f}"
                                                    for k, v in p["A"].items()) or "-",
                     "R2 without correction": p0["r2"] if p["A"] else np.nan,
                     "Accuracy without correction": p0["accuracy"] if p["A"] else np.nan})
    return {"lines": lines, "plain": plain, "summary": pd.DataFrame(rows),
            "y_bead": y_bead, "ref_wet": ref, "rm": rms, "cols": cols,
            "df_col": df_col, "loi_col": loi_col, "corrections": corrections}


def quantify(table, cal, names):
    """Concentrations of every row (wet, as-received basis).
    Correcting elements are taken from their own (uncorrected) lines, as in
    the paper (Ca and Mg show no matrix effect)."""
    cols, lines = cal["cols"], cal["lines"]
    dil = table[cal["df_col"]].astype(float)
    loi = (table[cal["loi_col"]].astype(float) if cal["loi_col"]
           else pd.Series(np.nan, index=table.index))
    bead = pd.DataFrame(index=table.index)
    for ox, p in cal["plain"].items():
        bead[ox] = predict(p, table[cols[ox]])
    for ox, p in lines.items():
        if p["A"]:
            bead[ox] = predict(p, table[cols[ox]], bead[list(p["A"])])
    dry = bead.mul(dil, axis=0)
    total_dry = dry.sum(axis=1, min_count=1)
    complete = len(bead.columns) >= 10
    base = total_dry if complete else pd.Series(100.0, index=table.index)
    wet = dry.mul((base - loi.fillna(0)) / base, axis=0)
    out = wet.copy()
    if "Cr2O3" in out:
        out["Cr"] = out["Cr2O3"] / CR2O3_PER_CR * 1e4
    if "NiO" in out:
        out["Ni"] = out["NiO"] / NIO_PER_NI * 1e4
    out["LOI"] = loi
    out["Total"] = wet[[c for c in OXIDES if c in wet]].sum(axis=1) + loi.fillna(0)
    if "MgO" in out and "Fe2O3t" in out:
        mg = out["MgO"] / 40.304
        fe = 2 * out["Fe2O3t"] / 159.688
        out["Mg#"] = 100 * mg / (mg + fe)
    plain_fe = None
    if "Fe2O3t" in lines and lines["Fe2O3t"]["A"]:
        b0 = predict(cal["plain"]["Fe2O3t"], table[cols["Fe2O3t"]])
        plain_fe = pd.Series(b0, index=table.index) * dil * (base - loi.fillna(0)) / base
    out.insert(0, "Sample", names)
    return out, plain_fe, complete


# ---------------- plots ----------------
def plot_lines(cal, table, style="dark", ncol=4):
    """Calibration lines: bead concentration vs X-ray intensity.
    For matrix-corrected oxides the corrected intensities are shown as
    filled symbols and the uncorrected ones as open symbols."""
    s = STYLES[style]
    ox_list = [o for o in OXIDES if o in cal["lines"]]
    n = len(ox_list)
    ncol = min(ncol, n)
    nrow = int(np.ceil(n / ncol))
    fig = _figure((2.75 * ncol, 2.5 * nrow + 0.4))
    fig.patch.set_facecolor(s["bg"])
    axes = np.atleast_1d(fig.subplots(nrow, ncol)).ravel()
    um = {"JP-1", "JP-2", "UB-N", "OKUM"}
    for ax, ox in zip(axes, ox_list):
        p, p0 = cal["lines"][ox], cal["plain"][ox]
        idx = p["bead_calc"].index
        i = table.loc[idx, cal["cols"][ox]].astype(float)
        y = cal["y_bead"].loc[idx, ox]
        is_um = cal["rm"][idx].isin(um).values
        if p["A"]:
            w = cal["y_bead"].loc[idx, list(p["A"])]
            ic = i * (1 + sum(p["A"][c] * w[c] for c in p["A"]))
            ax.scatter(i, y, s=22, facecolor="none", edgecolor=s["muted"], lw=0.8,
                       zorder=3, label="uncorrected")
            ax.scatter(ic, y, s=22, color="#4FB39A", edgecolor=s["edge"], lw=0.5,
                       zorder=4, label="Ca-Mg corrected" if set(p["A"]) == {"CaO", "MgO"}
                       else "corrected")
            xx = np.linspace(0, max(i.max(), ic.max()) * 1.04, 20)
            ax.plot(xx, p0["a"] * xx + p0["b"], color=s["muted"], lw=0.8, ls="--", zorder=2)
            ax.plot(xx, p["a"] * xx + p["b"], color=s["line"], lw=float(_APP["line_width"]),
                    zorder=2)
            ax.legend(fontsize=_APP["font_legend"] - 1, frameon=False, loc="upper left",
                      labelcolor=s["fg"])
            txt = f"R² = {p0['r2']:.4f} → {p['r2']:.4f}"
        else:
            ax.scatter(i[~is_um], y[~is_um], s=20, color="#6FA8DC", edgecolor=s["edge"],
                       lw=0.5, zorder=4)
            ax.scatter(i[is_um], y[is_um], s=26, color="#E69F00", edgecolor=s["edge"],
                       lw=0.5, zorder=5, marker="D")
            xx = np.linspace(0, i.max() * 1.04, 20)
            ax.plot(xx, p["a"] * xx + p["b"], color=s["line"], lw=float(_APP["line_width"]),
                    zorder=2)
            txt = f"R² = {p['r2']:.4f}"
        ax.text(0.97, 0.05, txt, transform=ax.transAxes, ha="right", va="bottom",
                color=s["fg"], fontsize=_APP["font_tick"])
        _style_axes(ax, s, "X-ray intensity", "Conc. in bead (wt%)")
        ax.set_title(label(ox), color=s["fg"], fontsize=_APP["font_axis"] + 1,
                     family=_APP["font_family"], fontweight="bold")
    for ax in axes[n:]:
        ax.set_visible(False)
    fig.tight_layout()
    return fig


def plot_fe_deviation(cal, style="dark"):
    """Like Fig. 4b of the paper: deviation (wet, wt%) of T-Fe2O3 for each
    standard, before and after matrix correction."""
    s = STYLES[style]
    p, p0 = cal["lines"]["Fe2O3t"], cal["plain"]["Fe2O3t"]
    idx = p0["deviation"].index
    names = cal["rm"][idx].tolist()
    fig = _figure((max(6.0, 0.32 * len(idx) + 1.5), 3.4))
    fig.patch.set_facecolor(s["bg"])
    ax = fig.subplots()
    x = np.arange(len(idx))
    ax.axhline(0, color=s["line"], lw=float(_APP["line_width"]))
    ax.scatter(x, p0["deviation"].values, s=30, facecolor="none", edgecolor="#E05252",
               lw=1.1, label="without correction", zorder=3)
    if p["A"]:
        ax.scatter(x, p["deviation"].values, s=30, color="#4FB39A", edgecolor=s["edge"],
                   lw=0.5, label="with matrix correction", zorder=4)
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=90)
    ax.set_xlim(-0.7, len(idx) - 0.3)
    ax.grid(axis="y", color=s["grid"], lw=0.6, zorder=0)
    _style_axes(ax, s, None, "T-Fe2O3 calc. - ref. (wt%)")
    ax.tick_params(axis="x", labelrotation=90)
    leg = ax.legend(fontsize=_APP["font_legend"], frameon=False, loc="upper right")
    for t in leg.get_texts():
        t.set_color(s["fg"])
    fig.tight_layout()
    return fig
