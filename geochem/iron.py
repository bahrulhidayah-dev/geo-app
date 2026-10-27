# geochem/iron.py
# Iron split: FeO and Fe2O3 (wt%) from total iron, for the CIPW norm and the
# diagrams that need both (Verma et al. 2006). Part of GeoChem App (GPL-3.0).
#
# Methods (chosen in Settings):
#   fixed              Fe3+/Fe(total) = r from Settings [App convention]
#   lemaitre_volcanic  Le Maitre (1976): Ox = 0.93 - 0.0042 SiO2 - 0.022 (Na2O + K2O)
#   lemaitre_plutonic  Le Maitre (1976): Ox = 0.88 - 0.0016 SiO2 - 0.027 (Na2O + K2O)
#                      Ox = FeO / (FeO + Fe2O3), weight ratio
#   middlemost         Middlemost (1989) Table I: standard Fe2O3/FeO (weight
#                      ratio) for each TAS field of Le Bas et al. (1986)
#
# Every method gives R = Fe2O3/FeO (weight ratio) for each sample. With total
# iron T expressed as FeO (FeOt = FeO + 0.8998 Fe2O3):
#   FeO = T / (1 + 0.8998 R)   and   Fe2O3 = R * FeO

import numpy as np
import pandas as pd

from .calc import FEO_PER_FE2O3, tas_xy

METHODS = ("fixed", "lemaitre_volcanic", "lemaitre_plutonic", "middlemost")

METHOD_LABELS = {
    "fixed": "Fixed Fe3+/Fe(total) ratio",
    "lemaitre_volcanic": "Le Maitre (1976), volcanic rocks",
    "lemaitre_plutonic": "Le Maitre (1976), plutonic rocks",
    "middlemost": "Middlemost (1989), standard ratio per TAS field (volcanic rocks)",
}

# Le Maitre (1976), p. 188: regressions of Ox = FeO/(FeO + Fe2O3) on SiO2 and
# Na2O + K2O for 12,962 volcanic and 9,604 plutonic rocks.
LE_MAITRE = {"lemaitre_volcanic": (0.93, 0.0042, 0.022),
             "lemaitre_plutonic": (0.88, 0.0016, 0.027)}

# Middlemost (1989), Table I and section 4: standard Fe2O3/FeO (weight ratio).
# Keys are TAS field names of Le Bas et al. (1986) in lower case, no spaces.
MIDDLEMOST = {
    "picrobasalt": 0.15, "basalt": 0.20, "basalticandesite": 0.30,
    "andesite": 0.35, "dacite": 0.40, "rhyolite": 0.50,
    "trachybasalt": 0.30, "basaltictrachyandesite": 0.35,
    "trachyandesite": 0.40, "trachyte/trachydacite": 0.50,
    "phonotephrite": 0.35, "tephriphonolite": 0.40, "phonolite": 0.50,
    # tephrite/basanite and foidite depend on Na2O + K2O (see _middlemost)
}


def spec(settings):
    """The iron-split choice from the settings, as a hashable tuple
    (method, fixed ratio, also replace measured values)."""
    m = settings.get("fe_method", "fixed")
    if m not in METHODS:
        m = "fixed"
    return (m, float(settings.get("fe3_ratio", 0.15)),
            bool(settings.get("fe_all", False)))


def _as_spec(iron):
    if isinstance(iron, (int, float, np.floating)):
        return ("fixed", float(iron), False)
    return tuple(iron)


def total_iron(df):
    """Total iron as FeO (wt%): FeOt, or Fe2O3t x 0.8998, or FeO + 0.8998 Fe2O3."""
    feo = df["FeO"] if "FeO" in df else pd.Series(np.nan, index=df.index)
    fe2o3 = df["Fe2O3"] if "Fe2O3" in df else pd.Series(np.nan, index=df.index)
    if "FeOt" in df:
        tot = df["FeOt"].copy()
    elif "Fe2O3t" in df:
        tot = df["Fe2O3t"] * FEO_PER_FE2O3
    else:
        tot = pd.Series(np.nan, index=df.index, dtype=float)
    calc_tot = feo.fillna(0) + FEO_PER_FE2O3 * fe2o3.fillna(0)
    calc_tot[feo.isna() & fe2o3.isna()] = np.nan
    return tot.fillna(calc_tot)


def _tas_inputs(df):
    """Anhydrous SiO2 and Na2O + K2O (Le Bas et al. 1986 basis) [App convention]."""
    xy = tas_xy(df, recalc=True)
    if xy is None:
        nan = pd.Series(np.nan, index=df.index)
        return nan, nan
    return xy["x"], xy["y"]


def _lemaitre(df, method):
    a, b, c = LE_MAITRE[method]
    si, alk = _tas_inputs(df)
    ox = (a - b * si - c * alk).clip(lower=0.05, upper=1.0)
    return (1 - ox) / ox


def tas_fields(df):
    """TAS field (Le Bas et al. 1986) of each sample, anhydrous basis."""
    from . import catalog, plotting      # imported here: catalog imports norms
    d = catalog.BY_ID["TAS"]
    coords = catalog.panel_data(d, 0, df, {"tas_recalc": True})
    return plotting.classify_panel(d, 0, coords)


def _middlemost(df):
    field = tas_fields(df).fillna("").str.lower().str.replace(" ", "")
    _, alk = _tas_inputs(df)
    r = field.map(MIDDLEMOST)
    # basanite/tephrite: 0.2 if Na2O + K2O < 6 %, else 0.3 (section 4)
    tb = field == "tephrite/basanite"
    r[tb] = np.where(alk[tb] < 6, 0.20, 0.30)
    # foidite: by Na2O + K2O (Table I)
    fo = field == "foidite"
    r[fo] = np.select([alk[fo] > 10, alk[fo] >= 7, alk[fo] >= 3], [0.4, 0.3, 0.2], 0.1)
    r[field.isin(["", "unclassified", "nodata"])] = np.nan
    return r.astype(float), field


def ratio(df, iron=0.15):
    """Fe2O3/FeO (weight ratio) for each sample, and the number of samples for
    which the chosen method could not be used (the fixed ratio is used)."""
    method, r_fixed, _ = _as_spec(iron)
    fixed = r_fixed / (FEO_PER_FE2O3 * (1 - r_fixed)) if r_fixed < 1 else np.inf
    if method == "fixed":
        return pd.Series(fixed, index=df.index, dtype=float), 0
    try:
        if method in LE_MAITRE:
            r = _lemaitre(df, method)
        else:
            r, _ = _middlemost(df)
    except (KeyError, ValueError):
        r = pd.Series(np.nan, index=df.index, dtype=float)
    missing = r.isna()
    return r.fillna(fixed), int(missing.sum())


def split(df, iron=0.15):
    """FeO and Fe2O3 (wt%) for every sample.

    Measured FeO and Fe2O3 are kept, unless the choice asks to standardise all
    samples. Otherwise total iron is split with the chosen method.
    Returns (FeO, Fe2O3, info) with info = dict(n_split, n_fallback, method)."""
    method, _, replace_all = _as_spec(iron)
    feo = df["FeO"] if "FeO" in df else pd.Series(np.nan, index=df.index)
    fe2o3 = df["Fe2O3"] if "Fe2O3" in df else pd.Series(np.nan, index=df.index)
    measured = feo.notna() & fe2o3.notna()
    keep = measured & (not replace_all)
    tot = total_iron(df)
    todo = ~keep & tot.notna()
    r, _ = ratio(df, iron)
    new_feo = tot / (1 + FEO_PER_FE2O3 * r)
    new_fe2o3 = r * new_feo
    out_feo = feo.where(keep, new_feo)
    out_fe2o3 = fe2o3.where(keep, new_fe2o3)
    n_fallback = 0
    if method != "fixed" and todo.any():
        _, n_fallback = ratio(df[todo], iron)
    info = dict(n_split=int(todo.sum()), n_fallback=n_fallback, method=method)
    return out_feo, out_fe2o3, info


def fe3_fraction(feo, fe2o3):
    """Fe3+/Fe(total), atomic, from FeO and Fe2O3 in wt%."""
    t = feo + FEO_PER_FE2O3 * fe2o3
    return (FEO_PER_FE2O3 * fe2o3) / t
