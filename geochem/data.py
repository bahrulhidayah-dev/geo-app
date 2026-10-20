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


def load_file(name, content):
    """Read CSV or Excel bytes into a table."""
    if name.lower().endswith(".csv"):
        return pd.read_csv(io.BytesIO(content))
    return pd.read_excel(io.BytesIO(content))


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


def map_columns(df):
    """Return {canonical name: column name in the file} for recognised columns."""
    lookup = {}
    for canon, keys in ALIASES.items():
        for k in keys:
            lookup.setdefault(k, canon)
    found = {}
    for col in df.columns:
        canon = lookup.get(_key(col))
        if canon and canon not in found and pd.api.types.is_numeric_dtype(df[col]):
            found[canon] = col
    return found


def standardize(df):
    """Copy of the table with recognised columns renamed to canonical names."""
    mapping = map_columns(df)
    return df.rename(columns={v: k for k, v in mapping.items()}), mapping
