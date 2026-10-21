# geochem/plotting.py
# Plotting engine: catalogue diagrams (GCDkit geometry, binary and ternary,
# single plots and plates), free XY and ternary plots and spider diagrams.
# Appearance (fonts, label orientation, line widths ...) is set once per run
# with set_appearance(). Part of GeoChem App (GPL-3.0).

import base64
import io
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
from matplotlib.figure import Figure
import numpy as np
import pandas as pd
from matplotlib.path import Path as MplPath

DIAGRAM_DIR = Path(__file__).parent / "diagrams"
SQRT3_2 = np.sqrt(3) / 2

STYLES = {
    "dark": {"bg": "#18202E", "fg": "#DCE2EC", "muted": "#8994A8",
             "line": "#5C6A82", "grid": "#26324A", "edge": "#0E141F",
             "field": "#6FA8DC", "poly_alpha": 0.18},
    "light": {"bg": "#FFFFFF", "fg": "#1B2333", "muted": "#5B6577",
              "line": "#7A8699", "grid": "#E5E9EF", "edge": "#1B2333",
              "field": "#4C86C6", "poly_alpha": 0.15},
    "publication": {"bg": "#FFFFFF", "fg": "#111111", "muted": "#3A3A3A",
                    "line": "#222222", "grid": "#E6E6E6", "edge": "#111111",
                    "field": "#9A9A9A", "poly_alpha": 0.25},
}
STYLES["screen"] = STYLES["dark"]          # backward compatibility

APPEARANCE_DEFAULT = {
    "font_family": "sans-serif",   # or "serif"
    "font_axis": 9.0,              # axis titles
    "font_tick": 8.0,              # tick labels
    "font_field": 1.0,             # multiplier for field names in diagrams
    "font_legend": 8.0,
    "font_point": 7.0,             # sample labels
    "field_labels": "template",    # template | horizontal | hidden
    "tick_rotation_x": 0,          # degrees
    "ylabel_rotation": "vertical",  # vertical | horizontal
    "line_width": 0.9,             # diagram boundaries
    "marker_edge": 0.7,
    "grid": False,                 # grid in classification diagrams
    "panel_titles": True,
    "size_scale": 1.0,             # figure size multiplier
}
_APP = dict(APPEARANCE_DEFAULT)


def set_appearance(values):
    """Set appearance options for all following plots."""
    _APP.clear()
    _APP.update(APPEARANCE_DEFAULT)
    _APP.update({k: v for k, v in (values or {}).items() if k in APPEARANCE_DEFAULT})


def load_diagram(filename):
    with open(DIAGRAM_DIR / filename, encoding="utf-8") as f:
        return json.load(f)


# ---------------- shared helpers ----------------
def _figure(size):
    k = float(_APP["size_scale"])
    fig = Figure(figsize=(size[0] * k, size[1] * k))
    fig.patch.set_alpha(1)
    return fig


def _style_axes(ax, s, xlab=None, ylab=None):
    ax.set_facecolor(s["bg"])
    for sp in ax.spines.values():
        sp.set_color(s["line"])
    ax.tick_params(colors=s["fg"], labelsize=_APP["font_tick"])
    ff = _APP["font_family"]
    for lab in ax.get_xticklabels() + ax.get_yticklabels():
        lab.set_family(ff)
    if _APP["tick_rotation_x"]:
        rot = float(_APP["tick_rotation_x"])
        ax.tick_params(axis="x", labelrotation=rot)
        for lab in ax.get_xticklabels():
            lab.set_ha("right" if 0 < rot < 90 else "center")
    if xlab is not None:
        ax.set_xlabel(xlab, color=s["fg"], fontsize=_APP["font_axis"], family=ff)
    if ylab is not None:
        if _APP["ylabel_rotation"] == "horizontal":
            ax.set_ylabel(ylab, color=s["fg"], fontsize=_APP["font_axis"], family=ff,
                          rotation=0, ha="right", va="center")
        else:
            ax.set_ylabel(ylab, color=s["fg"], fontsize=_APP["font_axis"], family=ff)


def _new_axes(style, size=(6.2, 4.8)):
    s = STYLES[style]
    # Figure objects (not pyplot) are safe to build in background threads,
    # which Streamlit uses for deferred downloads.
    fig = _figure(size)
    ax = fig.subplots()
    fig.patch.set_facecolor(s["bg"])
    _style_axes(ax, s)
    return fig, ax, s


def _draw_points(ax, x, y, sty, s, labels=None):
    """Draw samples with their own colour, symbol and size.
    sty comes from symbols.resolve(): columns group, colour, marker, size, filled."""
    x = pd.Series(np.asarray(x, dtype=float), index=sty.index)
    y = pd.Series(np.asarray(y, dtype=float), index=sty.index)
    ew = float(_APP["marker_edge"])
    seen = set()
    for (g, c, m, sz, f), part in sty.groupby(
            ["group", "colour", "marker", "size", "filled"], sort=False):
        idx = part.index
        kw = dict(s=sz ** 2, marker=m, zorder=4, linewidth=ew)
        if m in ("+", "x"):
            kw.update(color=c, linewidth=max(ew, 1.0) * 1.6)
        elif f:
            kw.update(facecolor=c, edgecolor=s["edge"])
        else:
            kw.update(facecolor="none", edgecolor=c, linewidth=max(ew, 1.0) * 1.6)
        ax.scatter(x.loc[idx], y.loc[idx], label=None if g in seen else g, **kw)
        seen.add(g)
    if labels is not None:
        for i in sty.index:
            if pd.notna(x.at[i]) and pd.notna(y.at[i]):
                ax.annotate(str(labels.at[i]), (x.at[i], y.at[i]),
                            xytext=(4, 3), textcoords="offset points",
                            fontsize=_APP["font_point"], color=s["fg"], zorder=5,
                            family=_APP["font_family"])


def _legend(ax, s, title=None, where="upper right"):
    handles, labels = ax.get_legend_handles_labels()
    if len(labels) > 1 and where != "hidden":
        fs = _APP["font_legend"]
        if where == "outside":
            leg = ax.legend(fontsize=fs, title=title, title_fontsize=fs,
                            frameon=False, loc="upper left",
                            bbox_to_anchor=(1.01, 1.0))
        else:
            leg = ax.legend(fontsize=fs, title=title, title_fontsize=fs,
                            frameon=False, loc=where)
        for t in leg.get_texts():
            t.set_color(s["fg"])
            t.set_family(_APP["font_family"])
        if leg.get_title():
            leg.get_title().set_color(s["muted"])


# ---------------- free XY plot ----------------
def plot_binary(df, x_col, y_col, sty, labels=None, log_x=False, log_y=False,
                style="dark", size=(6.2, 4.8), legend_title=None,
                legend="upper right"):
    fig, ax, s = _new_axes(style, size)
    _draw_points(ax, df[x_col], df[y_col], sty, s, labels)
    if log_x:
        ax.set_xscale("log")
    if log_y:
        ax.set_yscale("log")
    _style_axes(ax, s, x_col, y_col)
    ax.grid(color=s["grid"], lw=0.6)
    ax.set_axisbelow(True)
    _legend(ax, s, legend_title, legend)
    fig.tight_layout()
    return fig


# ---------------- free ternary plot ----------------
def _tern_xy(a, b, c):
    """Fractions (a + b + c = 1) to plot coordinates.
    GCDkit apex order: a left, b top, c right."""
    return c + b / 2, b * SQRT3_2


def plot_ternary(abc, apices, sty, labels=None, grid=True, style="dark",
                 size=(5.8, 5.2), legend_title=None, legend="upper right"):
    """Free ternary plot. abc: columns a, b, c in % (rows sum to 100),
    as returned by calc.ternary_closure. apices: three axis labels."""
    s = STYLES[style]
    fig = _figure(size)
    fig.patch.set_facecolor(s["bg"])
    ax = fig.subplots()
    ax.set_facecolor(s["bg"])
    ax.set_aspect("equal")
    ax.axis("off")
    ff = _APP["font_family"]
    lw = float(_APP["line_width"])
    if grid:
        ft = _APP["font_tick"] * 0.9
        for k in (0.2, 0.4, 0.6, 0.8):
            m = 1 - k
            # lines of equal a, b and c; each family is labelled on one edge
            for (p0, p1, lab, off, ha) in (
                    ((k, m, 0), (k, 0, m), (k, 0, m), (0, -0.035), "center"),   # a: bottom
                    ((m, k, 0), (0, k, m), (m, k, 0), (-0.03, 0), "right"),     # b: left
                    ((m, 0, k), (0, m, k), (0, m, k), (0.03, 0), "left")):      # c: right
                x0, y0 = _tern_xy(*p0)
                x1, y1 = _tern_xy(*p1)
                ax.plot([x0, x1], [y0, y1], color=s["grid"], lw=0.6, zorder=1)
                lx, ly = _tern_xy(*lab)
                ax.text(lx + off[0], ly + off[1], f"{k * 100:.0f}", ha=ha, va="center",
                        color=s["muted"], fontsize=ft, family=ff)
    ax.plot([0, 1, 0.5, 0], [0, 0, SQRT3_2, 0], color=s["fg"], lw=lw * 1.2, zorder=2)
    fs = _APP["font_axis"]
    a, b, c = apices
    ax.text(-0.02, -0.07, a, ha="right", va="top", color=s["fg"], fontsize=fs, family=ff)
    ax.text(0.5, SQRT3_2 + 0.035, b, ha="center", va="bottom", color=s["fg"],
            fontsize=fs, family=ff)
    ax.text(1.02, -0.07, c, ha="left", va="top", color=s["fg"], fontsize=fs, family=ff)
    f = abc[["a", "b", "c"]].astype(float) / 100
    x, y = _tern_xy(f["a"], f["b"], f["c"])
    _draw_points(ax, x, y, sty.loc[abc.index], s,
                 None if labels is None else labels.loc[abc.index])
    ax.set_xlim(-0.1, 1.1)
    ax.set_ylim(-0.12, SQRT3_2 + 0.1)
    _legend(ax, s, legend_title, legend)
    fig.tight_layout()
    return fig


# ---------------- spider ----------------
def plot_spider(norm_df, reference, sty, style="dark", size=(6.2, 4.6),
                legend_title=None, legend="upper right"):
    fig, ax, s = _new_axes(style, size)
    els = list(norm_df.columns)
    x = np.arange(len(els))
    seen = set()
    for r in norm_df.index:
        vals = norm_df.loc[r].to_numpy(dtype=float)
        if np.isnan(vals).all():
            continue
        g, c, mk, sz, f = sty.loc[r, ["group", "colour", "marker", "size", "filled"]]
        # dotted segments bridge missing elements, solid where data exist
        m = ~np.isnan(vals)
        ax.plot(x[m], vals[m], color=c, lw=0.9, ls=":", alpha=0.6, zorder=2)
        kw = dict(ms=max(sz * 0.55, 2.5), mew=0.5)
        if mk in ("+", "x"):
            kw.update(mec=c)
        elif f:
            kw.update(mfc=c, mec=s["edge"])
        else:
            kw.update(mfc="none", mec=c)
        ax.plot(x, vals, color=c, lw=1.2, marker=mk, zorder=3,
                label=None if g in seen else g, **kw)
        seen.add(g)
    ax.axhline(1, color=s["muted"], lw=0.8, ls="--", zorder=1)
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(els)
    ax.set_xlim(-0.5, len(els) - 0.5)
    _style_axes(ax, s, None, f"Sample / {reference['normalizer']}")
    ax.grid(color=s["grid"], lw=0.6, which="major")
    ax.set_axisbelow(True)
    _legend(ax, s, legend_title, legend)
    fig.tight_layout()
    return fig


# ---------------- catalogue diagrams (GCDkit geometry) ----------------
def _ternary_points(abc):
    a, b, c = (abc[k].astype(float) for k in ("a", "b", "c"))
    tot = a + b + c
    b, c = b / tot, c / tot
    return c + b / 2, b * SQRT3_2


def panel_xy(diagram, i, coords):
    """Plot coordinates (x, y) for panel i from calculated coordinates."""
    if diagram["panels"][i]["kind"] == "ternary":
        return _ternary_points(coords)
    return coords["x"].astype(float), coords["y"].astype(float)


FIELD_FIX = {"granodirite": "granodiorite"}   # typo in the GCDkit template


def classify_panel(diagram, i, coords):
    """Field name for each sample in panel i, or None if the panel has no fields."""
    geom = diagram["geometry"][i]
    if not geom.get("fields"):
        return None
    x, y = panel_xy(diagram, i, coords)
    lx, ly = diagram.get("field_log", (False, False))
    with np.errstate(divide="ignore", invalid="ignore"):
        px = np.log10(x.where(x > 0)) if lx else x
        py = np.log10(y.where(y > 0)) if ly else y
    pts = np.column_stack([px.to_numpy(float), py.to_numpy(float)])
    ok = ~np.isnan(pts).any(axis=1)
    names = pd.Series("Unclassified", index=coords.index, dtype=object)
    names[~ok] = "No data"
    for fld in geom["fields"]:
        path = MplPath(np.column_stack([fld["x"], fld["y"]]))
        inside = np.zeros(len(pts), dtype=bool)
        inside[ok] = path.contains_points(pts[ok], radius=1e-9)
        nm = FIELD_FIX.get(fld["name"], fld["name"])
        names[inside & (names == "Unclassified")] = nm[:1].upper() + nm[1:]
    return names


def _halign(adj):
    try:
        a = float(adj)
    except (TypeError, ValueError):
        a = 0.5
    return "left" if a < 0.25 else ("right" if a > 0.75 else "center")


def _draw_geometry(ax, geom, s, ternary, xlim, log_x, log_y):
    n0 = (len(ax.lines), len(ax.texts), len(ax.patches), len(ax.collections))
    lw = float(_APP["line_width"])
    for poly in geom.get("polygons", []):
        ax.fill(poly["x"], poly["y"], color=s["field"], alpha=s["poly_alpha"],
                lw=0, zorder=1)
    for k, ln in enumerate(geom.get("lines", [])):
        frame = ternary and k == 0
        col = s["fg"] if frame else (s["line"] if ln.get("role") != "minor" else s["muted"])
        kw = dict(color=col, lw=lw * (1.2 if frame else 1.0),
                  ls="--" if ln.get("dash") else "-", zorder=2)
        if "abline" in ln:
            ab = ln["abline"]
            if ab.get("h") is not None:
                ax.axhline(ab["h"], **kw)
            elif ab.get("v") is not None:
                ax.axvline(ab["v"], **kw)
            else:
                x0, x1 = sorted(xlim)
                if log_x and log_y:
                    xs = np.logspace(np.log10(x0), np.log10(x1), 50)
                    ys = 10 ** (ab["a"] + ab["b"] * np.log10(xs))
                else:
                    xs = np.linspace(x0, x1, 50)
                    ys = ab["a"] + ab["b"] * xs
                ax.plot(xs, ys, **kw)
        elif ln.get("lwd", 1) >= 5:             # broad band, e.g. terrestrial array
            ax.plot(ln["x"], ln["y"], color=s["muted"], lw=ln["lwd"], alpha=0.35,
                    solid_capstyle="butt", zorder=1)
        else:
            ax.plot(ln["x"], ln["y"], **kw)
    for pt in geom.get("points", []):
        ax.scatter(pt["x"], pt["y"], marker="s", s=22, color=s["muted"], zorder=3)
    mode = _APP["field_labels"]
    if mode != "hidden":
        for t in geom.get("texts", []):
            rot = t.get("rot", 0) if mode == "template" else 0
            ax.text(t["x"], t["y"], t["text"], rotation=rot, rotation_mode="anchor",
                    ha=_halign(t.get("adj")), va="center",
                    fontsize=6.8 * float(t.get("size") or 1) * float(_APP["font_field"]),
                    color=s["muted"], zorder=3, clip_on=True,
                    family=_APP["font_family"])
    # Template items often reach beyond the axes (they are clipped); keep them
    # out of the layout so the saved figure has no empty border.
    for art in (ax.lines[n0[0]:] + ax.texts[n0[1]:] + ax.patches[n0[2]:]
                + ax.collections[n0[3]:]):
        art.set_in_layout(False)


def plot_catalog(diagram, coords_list, sty, labels=None, style="dark",
                 legend_title=None, legend="upper right", panel_size=(4.6, 3.9),
                 only=None):
    """Draw a catalogue diagram (one panel or a plate of panels).
    coords_list: one DataFrame (or None if data are missing) per panel."""
    s = STYLES[style]
    idx = [only] if only is not None else list(range(len(diagram["panels"])))
    n = len(idx)
    ncol = 1 if n == 1 else (2 if n in (2, 4) else (4 if n > 9 else 3))
    nrow = int(np.ceil(n / ncol))
    fig = _figure((panel_size[0] * ncol, panel_size[1] * nrow))
    fig.patch.set_facecolor(s["bg"])
    axes = np.atleast_1d(fig.subplots(nrow, ncol)).ravel()
    for ax in axes[n:]:
        ax.set_visible(False)
    ff = _APP["font_family"]
    for ax, i in zip(axes, idx):
        p, geom = diagram["panels"][i], diagram["geometry"][i]
        ax.set_facecolor(s["bg"])
        ternary = p["kind"] == "ternary"
        xlim = geom.get("xlim") or [0, 1]
        ylim = geom.get("ylim") or [0, 1]
        if ternary:
            ax.set_aspect("equal")
            ax.axis("off")
            xlim, ylim = [-0.06, 1.06], [-0.1, SQRT3_2 + 0.08]
        else:
            if geom.get("log_x"):
                ax.set_xscale("log")
            if geom.get("log_y"):
                ax.set_yscale("log")
            _style_axes(ax, s, p.get("xlab") or geom.get("xlab"),
                        p.get("ylab") or geom.get("ylab"))
            if _APP["grid"]:
                ax.grid(color=s["grid"], lw=0.5)
                ax.set_axisbelow(True)
        _draw_geometry(ax, geom, s, ternary, xlim, geom.get("log_x"), geom.get("log_y"))
        if ternary:
            a, b, c = p["apices"]
            fs = _APP["font_axis"]
            ax.text(0, -0.05, a, ha="center", va="top", color=s["fg"], fontsize=fs, family=ff)
            ax.text(0.5, SQRT3_2 + 0.03, b, ha="center", va="bottom", color=s["fg"],
                    fontsize=fs, family=ff)
            ax.text(1, -0.05, c, ha="center", va="top", color=s["fg"], fontsize=fs, family=ff)
        coords = coords_list[i]
        if coords is not None:
            x, y = panel_xy(diagram, i, coords)
            if not ternary:
                if geom.get("log_x"):
                    x = x.where(x > 0)
                if geom.get("log_y"):
                    y = y.where(y > 0)
            _draw_points(ax, x, y, sty.loc[coords.index], s,
                         None if labels is None else labels.loc[coords.index])
        else:
            ax.text(0.5, 0.5, "Missing data", transform=ax.transAxes,
                    ha="center", va="center", color=s["muted"], fontsize=10)
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        if n > 1 and geom.get("name") and _APP["panel_titles"]:
            ax.set_title(geom["name"], color=s["fg"], fontsize=_APP["font_axis"] * 0.95,
                         loc="left", family=ff)
        if i == idx[0]:
            _legend(ax, s, legend_title, legend)
    fig.tight_layout()
    return fig


# ---------------- variation diagrams (Harker, MgO) ----------------
def _var_label(name, basis):
    """Axis label: oxides in wt% (anhydrous when recalculated), elements in ppm."""
    from .variation import OXIDES
    if name in OXIDES:
        return f"{name} (wt%{', anhydrous' if basis == 'anhydrous' else ''})"
    return f"{name} (ppm)"


def plot_variation(table, x, panels, sty, labels=None, style="dark", basis="anhydrous",
                   legend_title=None, legend="upper right", panel_size=(3.4, 2.8),
                   mg_lines=False, olivine=False, ncol=3):
    """Plate of variation diagrams: x (SiO2 or MgO) against every panel column.
    mg_lines / olivine: reference lines on the FeOt panel when x is MgO
    (Deschamps et al. 2013, Fig. 3b)."""
    from .variation import iso_mg_lines, olivine_line
    s = STYLES[style]
    n = len(panels)
    ncol = max(1, min(int(ncol), n))
    nrow = int(np.ceil(n / ncol)) if n else 1
    fig = _figure((panel_size[0] * ncol, panel_size[1] * nrow))
    fig.patch.set_facecolor(s["bg"])
    axes = np.atleast_1d(fig.subplots(nrow, ncol)).ravel()
    for ax in axes[n:]:
        ax.set_visible(False)
    xs = table[x]
    # one x range for every panel, so the panels can be compared directly
    xok = xs.dropna()
    if len(xok):
        pad_x = (xok.max() - xok.min()) * 0.06 or 1.0
        xr = (xok.min() - pad_x, xok.max() + pad_x)
    else:
        xr = (0.0, 1.0)
    for k, (ax, col) in enumerate(zip(axes, panels)):
        _style_axes(ax, s, _var_label(x, basis), _var_label(col, basis))
        if _APP["grid"]:
            ax.grid(color=s["grid"], lw=0.5)
            ax.set_axisbelow(True)
        ys = table[col]
        _draw_points(ax, xs, ys, sty.loc[table.index], s,
                     None if labels is None else labels.loc[table.index])
        ok = xs.notna() & ys.notna()
        ax.set_xlim(*xr)
        if ok.any():
            pad_y = (ys[ok].max() - ys[ok].min()) * 0.08 or 0.1
            ax.set_ylim(max(0.0, ys[ok].min() - pad_y), ys[ok].max() + pad_y)
        else:
            ax.text(0.5, 0.5, "No data", transform=ax.transAxes, ha="center",
                    va="center", color=s["muted"], fontsize=9)
        if x == "MgO" and col == "FeOt":
            x0, x1 = ax.get_xlim()
            y0, y1 = ax.get_ylim()
            lw = float(_APP["line_width"]) * 0.8
            if mg_lines:
                for mg, (mx, fy) in iso_mg_lines(mgo_max=max(x1, 1.0)).items():
                    ax.plot(mx, fy, color=s["muted"], lw=lw, ls="--", zorder=1)
                    xi = min(x1 * 0.97, mx[-1])
                    yi = xi * (fy[-1] / mx[-1])
                    if y0 < yi < y1:
                        ax.text(xi, yi, f"Mg# {mg:g}", fontsize=6.5, color=s["muted"],
                                ha="right", va="bottom", zorder=3, clip_on=True,
                                family=_APP["font_family"])
            if olivine:
                ox_, oy_ = olivine_line()
                ax.plot(ox_, oy_, color=s["line"], lw=lw * 1.4, zorder=1)
                # label where the line enters the plot, if it does
                yt = y1 * 0.985
                xt = ox_[0] * (1 - yt / oy_[1])
                if x0 < xt < x1:
                    ax.text(xt, yt, "Olivine", fontsize=6.5, color=s["fg"], ha="right",
                            va="top", zorder=3, family=_APP["font_family"])
            ax.set_xlim(x0, x1)
            ax.set_ylim(y0, y1)
        if k == 0:
            _legend(ax, s, legend_title, legend)
    fig.tight_layout()
    return fig


# ---------------- output ----------------
def figure_bytes(fig, fmt, dpi=300):
    buf = io.BytesIO()
    fig.savefig(buf, format=fmt, dpi=dpi, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    return buf.getvalue()


def figure_html(fig, max_width="100%"):
    """Figure as an inline SVG image. Nothing is served as a separate file,
    so browser download managers are not triggered."""
    buf = io.BytesIO()
    fig.savefig(buf, format="svg", bbox_inches="tight",
                facecolor=fig.get_facecolor())
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return (f'<img src="data:image/svg+xml;base64,{b64}" '
            f'style="width:100%;max-width:{max_width};height:auto;display:block;'
            f'border-radius:8px" alt="plot">')
