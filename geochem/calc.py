# geochem/calc.py
# Geochemical recalculations used by the diagrams. Part of GeoChem App (GPL-3.0).

import numpy as np
import pandas as pd

FEO_PER_FE2O3 = 0.8998    # 2 FeO / Fe2O3 molar mass ratio (143.69 / 159.69)
MW = {"SiO2": 60.084, "TiO2": 79.866, "Al2O3": 101.961, "Fe2O3": 159.688,
      "FeO": 71.844, "MnO": 70.937, "MgO": 40.304, "CaO": 56.077,
      "Na2O": 61.979, "K2O": 94.196, "P2O5": 141.945}
CATIONS = {"SiO2": 1, "TiO2": 1, "Al2O3": 2, "Fe2O3": 2, "FeO": 1, "MnO": 1,
           "MgO": 1, "CaO": 1, "Na2O": 2, "K2O": 2, "P2O5": 2}

# Oxide to element conversion factors (element mass fraction in the oxide)
OXIDE_TO_PPM = {"K": ("K2O", 0.8301), "Ti": ("TiO2", 0.5995),
                "P": ("P2O5", 0.4364)}

MAJORS_ANHYDROUS = ["SiO2", "TiO2", "Al2O3", "Fe2O3", "FeO", "Fe2O3t", "FeOt",
                    "MnO", "MgO", "CaO", "Na2O", "K2O", "P2O5"]


def feot(df):
    """Total iron as FeO (wt%), per sample: FeOt if given; else
    FeO + 0.8998 * Fe2O3; else 0.8998 * Fe2O3t. Files may mix forms
    (some rows with FeO and Fe2O3, others with total iron only)."""
    total = pd.Series(np.nan, index=df.index, dtype=float)
    if "FeOt" in df:
        total = df["FeOt"].astype(float).copy()
    sep = [c for c in ("FeO", "Fe2O3") if c in df]
    if sep:
        feo = df["FeO"] if "FeO" in df else pd.Series(0.0, index=df.index)
        fe2o3 = df["Fe2O3"] if "Fe2O3" in df else pd.Series(0.0, index=df.index)
        calc_t = feo.fillna(0) + FEO_PER_FE2O3 * fe2o3.fillna(0)
        calc_t[df[sep].isna().all(axis=1)] = np.nan
        total = total.fillna(calc_t)
    if "Fe2O3t" in df:
        total = total.fillna(FEO_PER_FE2O3 * df["Fe2O3t"])
    return total


def _iron_once(df):
    """Iron (wt%) counted once per sample for oxide totals: FeO + Fe2O3 where
    either was measured, otherwise Fe2O3t, otherwise FeOt."""
    iron = pd.Series(np.nan, index=df.index, dtype=float)
    sep = [c for c in ("FeO", "Fe2O3") if c in df]
    if sep:
        iron = df[sep].sum(axis=1, min_count=1)
    for c in ("Fe2O3t", "FeOt"):
        if c in df:
            iron = iron.fillna(df[c])
    return iron


def anhydrous(df):
    """Major oxides recalculated to 100 wt% on a volatile-free basis.
    Only oxides present in the file are used. Iron is counted once per sample
    (see _iron_once), so FeO/Fe2O3 and FeOt/Fe2O3t are never added together,
    also when a file mixes the two forms. Every iron column present is
    scaled with the same total."""
    cols = [c for c in MAJORS_ANHYDROUS if c in df]
    other = [c for c in cols if c not in ("FeO", "Fe2O3", "Fe2O3t", "FeOt")]
    total = df[other].sum(axis=1, min_count=1).add(_iron_once(df), fill_value=0)
    out = df[cols].div(total, axis=0) * 100
    return out, total


def tas_xy(df, recalc=True):
    """SiO2 and Na2O + K2O for the TAS diagram."""
    src = anhydrous(df)[0] if recalc else df
    if "SiO2" not in src or "Na2O" not in src or "K2O" not in src:
        return None
    return pd.DataFrame({"x": src["SiO2"], "y": src["Na2O"] + src["K2O"]})


def afm(df):
    """A, F, M in percent: A = Na2O + K2O, F = FeOt, M = MgO (wt%)."""
    if not all(c in df for c in ("Na2O", "K2O", "MgO")):
        return None
    a = df["Na2O"] + df["K2O"]
    f = feot(df)
    m = df["MgO"]
    s = a + f + m
    return pd.DataFrame({"A": a / s * 100, "F": f / s * 100, "M": m / s * 100})


def mg_number(df):
    """Mg# = 100 * Mg / (Mg + Fe2+), molar, with all iron taken as Fe2+."""
    if "MgO" not in df:
        return None
    mg = df["MgO"] / MW["MgO"]
    fe = feot(df) / MW["FeO"]
    return 100 * mg / (mg + fe)


def element_ppm(df, element):
    """Element concentration in ppm. K, Ti and P can come from their oxides (wt%)."""
    if element in df:
        return df[element]
    if element in OXIDE_TO_PPM:
        oxide, factor = OXIDE_TO_PPM[element]
        if oxide in df:
            return df[oxide] * factor * 10000
    return None


def normalize(df, reference):
    """Divide each element (ppm) by the reference value.
    Returns a table with one column per element available in the data."""
    out = {}
    for el, ref in reference["elements"].items():
        vals = element_ppm(df, el)
        if vals is not None:
            out[el] = vals / ref
    return pd.DataFrame(out, index=df.index)


def derived_table(df, recalc=True):
    """Useful calculated columns to show and export."""
    out = pd.DataFrame(index=df.index)
    anh, total = anhydrous(df)
    if not anh.empty:
        out["Major oxide total (wt%)"] = total
    fe = feot(df)
    if fe.notna().any():
        out["FeOt (wt%)"] = fe
    mg = mg_number(df)
    if mg is not None:
        out["Mg#"] = mg
    xy = tas_xy(df, recalc)
    if xy is not None:
        out["SiO2 (anhydrous)" if recalc else "SiO2"] = xy["x"]
        out["Na2O+K2O (anhydrous)" if recalc else "Na2O+K2O"] = xy["y"]
    return out


class MissingData(KeyError):
    """Raised when a diagram needs a column that is not in the data."""


def need(df, name):
    """Column by name. Trace elements K, Ti and P may come from their oxides,
    FeOt from any iron oxide. Raises MissingData if not available."""
    if name == "FeOt":
        v = feot(df)
        if v.notna().any():
            return v
        raise MissingData("FeOt (or FeO / Fe2O3)")
    if name in df:
        return df[name]
    v = element_ppm(df, name)
    if v is None:
        raise MissingData(name)
    return v


def mol(df, oxide):
    """Molecular proportion of an oxide (wt% / molar mass)."""
    if oxide == "FeOt":
        return need(df, "FeOt") / MW["FeO"]
    return need(df, oxide) / MW[oxide]


def milli(df, oxide):
    """Millication proportion (cations x 1000), as used by GCDkit."""
    if oxide == "FeOt":
        return 1000 * need(df, "FeOt") / MW["FeO"]
    return 1000 * CATIONS[oxide] * need(df, oxide) / MW[oxide]


def ternary_closure(df, specs):
    """Three components closed to 100 % for a ternary plot.

    specs: three (columns, factor) pairs for apices A, B and C. Each component
    is factor * (sum of its columns). Returns (abc, reasons):
    abc     - DataFrame with columns a, b, c in % (rows sum to 100),
              only for samples that can be plotted;
    reasons - Series (index = left-out samples) with the reason in English.
    """
    comp = {}
    missing = pd.Series(False, index=df.index)
    negative = pd.Series(False, index=df.index)
    for key, (cols, factor) in zip("abc", specs):
        vals = df[list(cols)].apply(pd.to_numeric, errors="coerce")
        missing |= vals.isna().any(axis=1)
        negative |= (vals < 0).any(axis=1)
        comp[key] = vals.sum(axis=1, min_count=1) * float(factor)
    abc = pd.DataFrame(comp)
    total = abc.sum(axis=1)
    reasons = pd.Series(pd.NA, index=df.index, dtype=object)
    reasons[(total <= 0) & ~missing & ~negative] = "zero total"
    reasons[negative & ~missing] = "negative value"
    reasons[missing] = "missing value"
    keep = reasons.isna()
    abc = abc[keep].div(total[keep], axis=0) * 100
    return abc, reasons[~keep]
