# geochem/screening.py
# Checks that run before a sample is named or plotted:
#   - "high-Mg" volcanic rocks (boninite, komatiite, meimechite, picrite) and
#     nephelinites, which IUGS says must be separated BEFORE using TAS
#     (Le Maitre et al. 2002, p. 34 and Fig. 2.13, after Le Bas 2000);
#   - freshness for TAS: H2O+ < 2 wt% and CO2 < 0.5 wt%
#     (Le Bas et al. 1986; Le Bas et al. 1992);
#   - ultramafic samples (by MgO or by the Rock type column);
#   - relative MgO deficit against the terrestrial array (Niu 2004).
# Part of GeoChem App (GPL-3.0).

import numpy as np
import pandas as pd

from . import calc

# Words in the Rock type column that mark plutonic or metamorphic ultramafic
# rocks. TAS and the high-Mg volcanic names do not apply to these rocks.
ULTRAMAFIC_WORDS = ("serpentin", "peridot", "dunit", "harzburg", "lherzol",
                    "wehrl", "pyroxenit", "ultramafic", "websterit", "troctolit")

# Terrestrial array, MgO/SiO2 = a + b * Al2O3/SiO2 (oxide weight ratios).
# Niu (2004) J. Petrology 45, Fig. 2a: intercept 1.107, slope -2.598.
# Oceanic (abyssal peridotite) array: intercept 1.019, slope -2.596.
TERRESTRIAL_ARRAY = (1.107, -2.598)
OCEANIC_ARRAY = (1.019, -2.596)

# Freshness limits for TAS (Le Bas et al. 1986, rule e; Le Bas et al. 1992, rule 4)
H2O_MAX, CO2_MAX = 2.0, 0.5
LOI_PROXY_MAX = H2O_MAX + CO2_MAX      # used only when H2O+ and CO2 are missing

HIGH_MG_NAMES = ("Boninite", "Komatiite", "Meimechite", "Picrite")


def _anh(df):
    """Anhydrous major oxides (100 wt% volatile-free)."""
    return calc.anhydrous(df)[0]


def _col(a, name):
    return a[name] if name in a else pd.Series(np.nan, index=a.index)


def high_mg_names(df):
    """IUGS names for "high-Mg" volcanic rocks, checked before TAS.

    Le Maitre et al. (2002), Fig. 2.13 (wt%, anhydrous):
      1. SiO2 > 52, MgO > 8, TiO2 < 0.5                    -> boninite
      2. 30 < SiO2 < 52, MgO > 18, Na2O + K2O < 2, TiO2 < 1 -> komatiite
                                                   TiO2 > 1 -> meimechite
      3. 30 < SiO2 < 52, MgO > 12, Na2O + K2O < 3           -> picrite
    Returns a text Series; empty text = not a high-Mg rock (use TAS)."""
    a = _anh(df)
    si, mg, ti = _col(a, "SiO2"), _col(a, "MgO"), _col(a, "TiO2")
    alk = _col(a, "Na2O") + _col(a, "K2O")
    out = pd.Series("", index=df.index, dtype=object)
    no_ti = ti.isna()
    mid_si = (si > 30) & (si < 52)
    # 3. picrite (checked first, so the stricter rules below overwrite it)
    out[mid_si & (mg > 12) & (alk < 3)] = "Picrite"
    # 2. komatiite / meimechite
    km = mid_si & (mg > 18) & (alk < 2)
    out[km & (ti < 1)] = "Komatiite"
    out[km & (ti >= 1)] = "Meimechite"
    out[km & no_ti] = "Komatiite or meimechite (TiO2 needed)"
    # 1. boninite
    bon = (si > 52) & (mg > 8)
    out[bon & (ti < 0.5)] = "Boninite"
    out[bon & no_ti & (out == "")] = "Boninite? (TiO2 needed)"
    return out


def nephelinite_names(df, iron, tas_field):
    """Nephelinite and melanephelinite fall in TAS fields F and U1 and must be
    separated with the CIPW norm (Le Bas 1989, in Le Maitre et al. 2002 p. 36):
    ne > 20 % -> nephelinite; ne < 20 % with ab present but < 5 % ->
    melanephelinite. Only samples in the foidite or basanite/tephrite fields
    are tested."""
    from . import norms        # imported here: the norm is slow, use it only if needed
    out = pd.Series("", index=df.index, dtype=object)
    field = tas_field.fillna("").str.lower()
    test = field.str.contains("foidite") | field.str.contains("basanite") | \
        field.str.contains("tephrite")
    test &= ~field.str.contains("phono")
    if not test.any():
        return out
    sub = df[test]
    try:
        n, _ = norms.cipw(sub, iron)
    except (KeyError, calc.MissingData, ValueError):
        return out
    ne, ab = n["Ne"].reindex(sub.index), n["Ab"].reindex(sub.index)
    res = pd.Series("", index=sub.index, dtype=object)
    res[ne > 20] = "Nephelinite"
    res[(ne <= 20) & (ab > 0) & (ab < 5)] = "Melanephelinite"
    out[sub.index] = res
    return out


def rock_type_ultramafic(df):
    """True where the Rock type (or Group) column names a plutonic or
    metamorphic ultramafic rock (serpentinite, peridotite, dunite,
    harzburgite, 'ultramafic' ...)."""
    hit = pd.Series(False, index=df.index)
    for col in ("Rock type", "Group"):
        if col not in df:
            continue
        txt = df[col].astype(str).str.lower()
        for w in ULTRAMAFIC_WORDS:
            hit |= txt.str.contains(w, regex=False)
    return hit


def ultramafic_mask(df, mgo_min=30.0):
    """Ultramafic samples: anhydrous MgO >= mgo_min, or an ultramafic rock type."""
    a = _anh(df)
    mg = _col(a, "MgO")
    return (mg >= mgo_min).fillna(False) | rock_type_ultramafic(df)


def freshness(df, high_mg=None):
    """Freshness for TAS after Le Bas et al. (1986): analyses with H2O+ > 2 wt%
    or CO2 > 0.5 wt% are suspect. Uses LOI > 2.5 wt% as a proxy when neither
    H2O+ nor CO2 was measured. The rule is withdrawn for picrite, komatiite,
    meimechite and boninite (Le Maitre et al. 2002, p. 33)."""
    out = pd.Series("Not checked (no H2O+, CO2 or LOI)", index=df.index, dtype=object)
    have_h, have_c = "H2O+" in df, "CO2" in df
    if have_h or have_c:
        h = df["H2O+"] if have_h else pd.Series(np.nan, index=df.index)
        c = df["CO2"] if have_c else pd.Series(np.nan, index=df.index)
        known = h.notna() | c.notna()
        out[known] = "Fresh"
        bad_h, bad_c = h > H2O_MAX, c > CO2_MAX
        out[bad_h] = "Suspect: H2O+ " + h[bad_h].round(2).astype(str) + " > 2 wt%"
        out[bad_c & ~bad_h] = "Suspect: CO2 " + c[bad_c & ~bad_h].round(2).astype(str) + " > 0.5 wt%"
        out[bad_c & bad_h] = "Suspect: H2O+ > 2 and CO2 > 0.5 wt%"
    if "LOI" in df:
        use = out.str.startswith("Not checked") & df["LOI"].notna()
        loi = df["LOI"]
        out[use & (loi <= LOI_PROXY_MAX)] = "Fresh (LOI proxy)"
        bad = use & (loi > LOI_PROXY_MAX)
        out[bad] = "Suspect: LOI " + loi[bad].round(2).astype(str) + " > 2.5 wt% (proxy)"
    if high_mg is not None:
        hm = high_mg.str.startswith(HIGH_MG_NAMES)
        out[hm & out.str.startswith("Suspect")] = "Rule withdrawn (high-Mg rock)"
    return out


def tas_names(df, tas_field, iron=0.15, mgo_min=30.0):
    """IUGS rock name for volcanic rocks, following the order of Le Maitre et
    al. (2002): ultramafic rock type -> not applicable; high-Mg rocks;
    nephelinites; otherwise the TAS field. Returns (name, high_mg).

    The high-Mg rules use chemistry only, so a peridotite or serpentinite also
    meets the komatiite rule. When such a sample has no Rock type, the name
    gets a reminder; with Rock type = serpentinite (etc.) it is not named."""
    hm = high_mg_names(df)
    neph = nephelinite_names(df, iron, tas_field)
    name = tas_field.astype(object).copy()
    name[neph != ""] = neph[neph != ""]
    name[hm != ""] = hm[hm != ""]
    rich = (_col(_anh(df), "MgO") >= mgo_min).fillna(False) & (hm != "")
    name[rich] = name[rich] + " (if volcanic; give Rock type for peridotites)"
    name[rock_type_ultramafic(df)] = "TAS not applicable (ultramafic rock)"
    return name, hm


def array_mgo_si(al_si, array=TERRESTRIAL_ARRAY):
    a, b = array
    return a + b * al_si


def mgo_deficit(df):
    """Relative MgO deficit (%) against the terrestrial array (Niu 2004):
    100 * [1 - (MgO/SiO2) / (1.107 - 2.598 * Al2O3/SiO2)].
    Assumes SiO2 and Al2O3 were immobile, as Niu (2004) did. Positive values
    mean MgO lost (or SiO2 gained). Oxide ratios do not change with
    anhydrous recalculation, so LOI does not affect the result."""
    if not all(c in df for c in ("MgO", "SiO2", "Al2O3")):
        return None
    ratio = df["MgO"] / df["SiO2"]
    ref = array_mgo_si(df["Al2O3"] / df["SiO2"])
    return 100 * (1 - ratio / ref)
