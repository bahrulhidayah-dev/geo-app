# geochem/data.py
# Reading, cleaning and recognising columns in geochemical data tables.
# Part of GeoChem App (GPL-3.0).

import io
import re

import pandas as pd

# Canonical names the app understands, with other spellings found in lab files.
ALIASES = {
    "SiO2": ["sio2"], "TiO2": ["tio2"], "Al2O3": ["al2o3"],
    "Fe2O3": ["fe2o3"], "FeO": ["feo"],
    "Fe2O3t": ["fe2o3t", "fe2o3tot", "fe2o3total", "fe2o3*", "tfe2o3"],
    "FeOt": ["feot", "feotot", "feototal", "feo*", "tfeo"],
    "MnO": ["mno"], "MgO": ["mgo"], "CaO": ["cao"], "Na2O": ["na2o"],
    "K2O": ["k2o"], "P2O5": ["p2o5"], "LOI": ["loi"],
    "H2O+": ["h2o+", "h2oplus", "h2op"], "CO2": ["co2"],
    "Cr2O3": ["cr2o3"], "NiO": ["nio"],
    "Latitude": ["latitude", "lat"], "Longitude": ["longitude", "lon", "long"],
}
TRACE = ["Ti", "K", "P", "Cs", "Rb", "Ba", "Th", "U", "Nb", "Ta", "La", "Ce", "Pb", "Pr", "Sr",
         "Nd", "Zr", "Hf", "Sm", "Eu", "Gd", "Tb", "Dy", "Y", "Ho", "Er", "Tm",
         "Yb", "Lu", "Cr", "Ni", "Co", "V", "Sc", "Cu", "Zn", "Ga", "Li"]
for _el in TRACE:
    ALIASES[_el] = [_el.lower()]


def _key(name):
    """Simplify a column name: 'SiO2 (wt%)' -> 'sio2', 'Fe2O3T_wt' -> 'fe2o3t'."""
    s = str(name).strip().lower()
    s = re.sub(r"\(.*?\)|\[.*?\]", "", s)
    s = re.sub(r"(wt\.?%|wt|ppm|ppb|%)", "", s)
    s = re.sub(r"[\s_\-.]", "", s)
    return s


def _as_text(series):
    """Cells as stripped text; empty cells become ''. (pandas 3 keeps NaN
    as missing in astype(str), so this is done explicitly.)"""
    return series.map(lambda v: "" if pd.isna(v) else str(v)).astype(object).str.strip()


def load_file(name, content, header_row=1):
    """Read CSV or Excel bytes into a table. header_row: the row (1 = first)
    that holds the column names; rows above it (titles, notes) are skipped."""
    skip = max(int(header_row or 1) - 1, 0)
    if name.lower().endswith(".csv"):
        return pd.read_csv(io.BytesIO(content), skiprows=skip)
    return pd.read_excel(io.BytesIO(content), skiprows=skip)


# ---------------- units ----------------
OXIDES = ["SiO2", "TiO2", "Al2O3", "Fe2O3", "FeO", "Fe2O3t", "FeOt", "MnO", "MgO",
          "CaO", "Na2O", "K2O", "P2O5", "LOI", "H2O+", "CO2", "Cr2O3", "NiO"]
UNITS = ["wt%", "ppm", "ppb"]
TO_PPM = {"wt%": 1e4, "ppm": 1.0, "ppb": 1e-3}


def expected_unit(canon):
    """Unit the app uses internally: wt% for oxides and LOI, ppm for elements."""
    if canon in OXIDES:
        return "wt%"
    if canon in TRACE:
        return "ppm"
    return None


def unit_from_text(text):
    """'ppb', 'ng/g' -> ppb; 'ppm', 'ug/g', 'mg/kg' -> ppm; 'wt%', '%' -> wt%."""
    t = str(text).strip().lower().replace("µ", "u").replace("μ", "u")
    if not t:
        return None
    if re.search(r"ppb|ng/g|ug/kg", t):
        return "ppb"
    if re.search(r"ppm|ug/g|mg/kg|g/t", t):
        return "ppm"
    if re.search(r"wt|%|mass", t):
        return "wt%"
    return None


def detect_units(raw):
    """Unit of each column, from its name ('La (ppb)', 'Cr_ppm', 'SiO2 wt%')
    or from a units row under the header ('wt%', 'ppm', 'ppb')."""
    units = {}
    first = raw.iloc[0] if len(raw) else None
    for col in raw.columns:
        u = unit_from_text(col) if re.search(r"ppm|ppb|wt|%|/g|/kg", str(col).lower()) else None
        if u is None and first is not None and isinstance(first[col], str):
            if not re.search(r"\d", first[col]):          # a word, not a number
                u = unit_from_text(first[col])
        if u:
            units[str(col).strip()] = u
    return units


def clean_data(raw):
    """Convert mostly-numeric columns to numbers.
    '<0.01', 'n.d.', 'bdl' become missing (NaN); decimal commas are accepted;
    rows without any number (units rows, empty rows) are removed.
    Returns the cleaned table and a report of every change."""
    df = raw.copy()
    df.columns = [str(c).strip() for c in df.columns]
    df = df.loc[:, [c for c in df.columns if not c.lower().startswith("unnamed")]]
    report = []
    converted, bad_cells = {}, {}
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            continue
        text = _as_text(df[col])
        fixed = text.where(~text.str.fullmatch(r"-?\d+,\d+"),
                           text.str.replace(",", ".", regex=False))
        numbers = pd.to_numeric(fixed, errors="coerce")
        if numbers.notna().mean() >= 0.5:
            converted[col] = numbers
            bad_cells[col] = text[numbers.isna() & (text != "")]
    for col, numbers in converted.items():
        df[col] = numbers

    # Rows with no numeric value at all (a units row such as "wt% / ppm",
    # or empty rows at the end of an Excel sheet) are removed and reported once.
    num_cols = df.select_dtypes(include="number").columns
    empty = (df[num_cols].isna().all(axis=1) if len(num_cols)
             else pd.Series(False, index=df.index))
    for col, bad in bad_cells.items():
        bad = bad[~empty.loc[bad.index]]
        if len(bad) > 0:
            report.append({"Column": col, "Cells set to missing": len(bad),
                           "Examples": ", ".join(sorted(set(bad))[:5])})
    if empty.any():
        names = _as_text(df.loc[empty, df.columns[0]]).replace("", "(blank)").tolist()
        report.append({"Column": "(whole row)",
                       "Cells set to missing": int(empty.sum()),
                       "Examples": "Rows removed, no numeric values: "
                                   + ", ".join(names[:5])})
        df = df.loc[~empty].reset_index(drop=True)
    return df, pd.DataFrame(report)


CANONICAL = list(ALIASES)                 # every name the app understands
ROLES = ["Sample", "Rock type", "Locality", "Group"]
AUTO, TEXT, IGNORE = "(auto)", "(text)", "(ignore)"


def guess(col):
    """Canonical name for a column name, or None."""
    lookup = {}
    for canon, keys in ALIASES.items():
        for k in keys:
            lookup.setdefault(k, canon)
    return lookup.get(_key(col))


def map_columns(df, overrides=None):
    """Return {canonical name: column name in the file} for recognised columns.
    overrides: {file column: canonical name, '(text)' or '(ignore)'}."""
    overrides = overrides or {}
    found = {}
    for col in df.columns:                 # the user's choices come first
        o = overrides.get(col)
        if o and o not in (AUTO, TEXT, IGNORE) and o not in found \
                and pd.api.types.is_numeric_dtype(df[col]):
            found[o] = col
    for col in df.columns:
        if overrides.get(col, AUTO) != AUTO or col in found.values():
            continue
        canon = guess(col)
        if canon and canon not in found and pd.api.types.is_numeric_dtype(df[col]):
            found[canon] = col
    return found


def standardize(df, setup=None, units=None, raw=None):
    """Copy of the table ready for the app.
    - recognised columns renamed to canonical names (SiO2, La ...);
    - values converted to wt% (oxides) or ppm (elements) when the file
      gives another unit;
    - the user's column setup applied: ignored columns removed, text
      columns kept as text, roles (Sample, Rock type, Locality, Group).
    Returns (table, mapping, unit report)."""
    setup = setup or {}
    overrides = setup.get("columns", {})
    unit_over = setup.get("units", {})
    units = dict(units or {})
    units.update({c: u for c, u in unit_over.items() if u in UNITS})
    df = df.copy()
    for col, o in overrides.items():
        if col not in df:
            continue
        if o == IGNORE:
            df = df.drop(columns=col)
        elif o == TEXT and raw is not None and col in raw:
            df[col] = _as_text(raw[col]).reindex(df.index)
    mapping = map_columns(df, overrides)
    report = []
    for canon, col in mapping.items():
        have, want = units.get(col), expected_unit(canon)
        if have and want and have != want:
            factor = TO_PPM[have] / TO_PPM[want]
            df[col] = df[col] * factor
            report.append({"Column": col, "Read as": canon, "Unit in file": have,
                           "Converted to": want, "Factor": factor})
    out = df.rename(columns={v: k for k, v in mapping.items()})
    # roles: the sample column goes first (all tables and results use it)
    roles = setup.get("roles", {})
    sample = roles.get("Sample")
    if sample in out.columns:
        out = out[[sample] + [c for c in out.columns if c != sample]]
    rename = {}
    for role in ROLES[1:]:
        col = roles.get(role)
        if col in out.columns and role not in out.columns:
            rename[col] = role
    out = out.rename(columns=rename)
    return out, mapping, pd.DataFrame(report)
