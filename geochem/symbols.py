# geochem/symbols.py
# Plotting symbols, colours and sizes for groups of samples.
# Follows the GCDkit idea: one table of styles per group, used by every
# diagram. Optional per-sample columns "Symbol", "Colour"/"Color" and
# "Size"/"cex" in the data file are also understood. Part of GeoChem App (GPL-3.0).

import matplotlib.colors as mcolors
import pandas as pd

# Friendly name -> matplotlib marker code
MARKERS = {
    "Circle": "o", "Square": "s", "Triangle up": "^", "Triangle down": "v",
    "Diamond": "D", "Pentagon": "p", "Hexagon": "h", "Star": "*",
    "Plus (thick)": "P", "Cross (thick)": "X", "Plus": "+", "Cross": "x",
}
LINE_MARKERS = {"+", "x"}          # drawn as lines, cannot be filled
MARKER_NAMES = list(MARKERS)

PALETTES = {
    "Default": ["#4FB39A", "#E3A857", "#6FA8DC", "#D9798F", "#A99BD8",
                "#C9B98B", "#7FC4D6", "#E08E5B"],
    # Okabe and Ito (2008), safe for colour-vision deficiencies
    "Colour-blind safe": ["#E69F00", "#56B4E9", "#009E73", "#F0E442",
                          "#0072B2", "#D55E00", "#CC79A7", "#999999"],
    "Greyscale": ["#111111", "#555555", "#888888", "#BBBBBB", "#FFFFFF"],
}
DEFAULT_SIZE = 7          # marker size in points (diameter)

# GCDkit / R colour codes 0-8 (see GCDkit cheat sheet)
R_COLOURS = {0: "white", 1: "black", 2: "red", 3: "green", 4: "blue",
             5: "cyan", 6: "magenta", 7: "yellow", 8: "grey"}
# R pch codes -> (marker, filled)
R_PCH = {0: ("s", False), 1: ("o", False), 2: ("^", False), 3: ("+", False),
         4: ("x", False), 5: ("D", False), 6: ("v", False), 8: ("*", True),
         15: ("s", True), 16: ("o", True), 17: ("^", True), 18: ("D", True),
         19: ("o", True), 20: ("o", True), 21: ("o", True), 22: ("s", True),
         23: ("D", True), 24: ("^", True), 25: ("v", True)}


def default_style(i, palette="Default"):
    cols = PALETTES[palette]
    return {"colour": cols[i % len(cols)],
            "symbol": MARKER_NAMES[i % 8],
            "size": DEFAULT_SIZE, "filled": True}


def auto_styles(groups, palette="Default", old=None):
    """Style table for the given group names. Existing entries in 'old'
    are kept so user choices survive when the data are reloaded."""
    old = old or {}
    return {g: dict(old.get(g, default_style(i, palette)))
            for i, g in enumerate(groups)}


def parse_colour(value):
    """Colour from a data-file cell: R code, English name or #hex."""
    if pd.isna(value):
        return None
    s = str(value).strip()
    try:
        code = int(float(s))
        return R_COLOURS.get(code)
    except ValueError:
        pass
    if mcolors.is_color_like(s):
        return s
    if mcolors.is_color_like(s.lower()):
        return s.lower()
    return None


def parse_symbol(value):
    """(marker, filled) from a data-file cell: R pch code or friendly name."""
    if pd.isna(value):
        return None
    s = str(value).strip()
    try:
        return R_PCH.get(int(float(s)))
    except ValueError:
        pass
    for name, code in MARKERS.items():
        if s.lower() in (name.lower(), code.lower()):
            return code, code not in LINE_MARKERS
    return None


def file_columns(df):
    """Names of per-sample style columns present in the data, if any."""
    cols = {c.lower(): c for c in df.columns}
    return {"colour": cols.get("colour") or cols.get("color") or cols.get("col"),
            "symbol": cols.get("symbol") or cols.get("pch"),
            "size": cols.get("size") or cols.get("cex")}


def resolve(df, group_col, table, use_file=False):
    """Per-sample drawing style.
    Returns a table (same index as df) with columns:
    group, colour, marker, size, filled."""
    if group_col is None:
        groups = pd.Series("All samples", index=df.index)
    else:
        groups = df[group_col].astype(str).fillna("(blank)")
    rows = []
    fc = file_columns(df) if use_file else {}
    for i in df.index:
        g = groups.at[i]
        st = table.get(g) or default_style(0)
        colour, marker = st["colour"], MARKERS.get(st["symbol"], "o")
        filled, size = st["filled"], float(st["size"])
        if fc.get("colour"):
            colour = parse_colour(df.at[i, fc["colour"]]) or colour
        if fc.get("symbol"):
            ps = parse_symbol(df.at[i, fc["symbol"]])
            if ps:
                marker, filled = ps
        if fc.get("size"):
            try:
                rel = float(df.at[i, fc["size"]])
                if rel > 0:
                    size = DEFAULT_SIZE * rel
            except (TypeError, ValueError):
                pass
        if marker in LINE_MARKERS:
            filled = False
        rows.append((g, colour, marker, size, filled))
    return pd.DataFrame(rows, index=df.index,
                        columns=["group", "colour", "marker", "size", "filled"])
