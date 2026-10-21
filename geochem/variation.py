# geochem/variation.py
# Variation diagrams: Harker diagrams (SiO2 on the x axis) and MgO variation
# diagrams (MgO on the x axis), one panel per major oxide, plus optional
# trace elements. Part of GeoChem App (GPL-3.0).
#
# Scientific basis (see docs/methods.md, chapter "Variation diagrams"):
# - Harker diagrams: SiO2 vs each oxide (Harker 1909, as cited in Rollinson
#   and Pease 2021, section 3.3); MgO for mafic and ultramafic suites
#   (Rollinson and Pease 2021, section 3.3.2).
# - MgO variation diagrams for mafic and ultramafic rocks and peridotites
#   (Niu 2004; Deschamps et al. 2013), with iso-Mg# lines and the olivine
#   line (Deschamps et al. 2013, Fig. 3b).
# - Major oxides on a 100 wt% volatile-free basis by default (Le Bas et al.
#   1986; Niu 2004; Deschamps et al. 2013). Trace elements are shown as
#   measured (App convention).

import numpy as np
import pandas as pd

from . import calc

# Order of the oxide panels (FeOt = total iron as FeO)
OXIDES = ["SiO2", "TiO2", "Al2O3", "FeOt", "MnO", "MgO", "CaO", "Na2O", "K2O", "P2O5"]
X_CHOICES = ("SiO2", "MgO")

# Molar masses (g/mol) for the Mg# and olivine lines
_M_MGO, _M_FEO, _M_SIO2 = 40.304, 71.844, 60.084


def oxide_values(df, basis="anhydrous"):
    """Major oxides (wt%) with total iron as FeOt.

    basis = "anhydrous": recalculated to 100 wt% without volatiles, with the
    same oxide set as the TAS recalculation (calc.anhydrous).
    basis = "as measured": the values of the file."""
    if basis == "anhydrous":
        src, _ = calc.anhydrous(df)
    else:
        src = df
    out = pd.DataFrame(index=df.index)
    for ox in OXIDES:
        if ox == "FeOt":
            fe = calc.feot(src)
            if fe.notna().any():
                out["FeOt"] = fe
        elif ox in src:
            out[ox] = src[ox]
    return out


def variation_table(df, x="SiO2", basis="anhydrous", extra=()):
    """Values for a variation-diagram plate.

    Returns (table, panels, missing):
    table   - DataFrame with the x column and one column per panel;
    panels  - y columns in plot order (oxides first, then extra elements);
    missing - oxides that are not in the file (their panels are skipped)."""
    if x not in X_CHOICES:
        raise ValueError(f"x must be one of {X_CHOICES}")
    ox = oxide_values(df, basis)
    if x not in ox:
        raise calc.MissingData(x)
    panels = [c for c in OXIDES if c != x and c in ox and ox[c].notna().any()]
    missing = [c for c in OXIDES if c != x and c not in panels]
    table = ox[[x] + panels].copy()
    for el in extra:
        v = calc.element_ppm(df, el)
        if v is not None and v.notna().any():
            table[el] = v
            panels.append(el)
    return table, panels, missing


def iso_mg_lines(mg_numbers=(85, 87.5, 90, 92.5, 95), mgo_max=55.0):
    """Lines of constant Mg# in FeOt-MgO space (wt%), all iron as Fe2+.
    Mg# = 100 Mg / (Mg + Fe), molar, gives FeOt = MgO (M_FeO/M_MgO)(100/Mg# - 1).
    Returns {Mg#: (MgO array, FeOt array)}."""
    mgo = np.linspace(0, mgo_max, 50)
    return {m: (mgo, mgo * (_M_FEO / _M_MGO) * (100.0 / m - 1)) for m in mg_numbers}


def olivine_line():
    """Olivine compositions from forsterite to fayalite in MgO-FeOt space
    (wt%). Mass mixing is linear, so the line joins the two end-members:
    Mg2SiO4 (MgO = 57.30 wt%, FeO = 0) and Fe2SiO4 (MgO = 0, FeO = 70.51 wt%)
    (Deschamps et al. 2013, Fig. 3b)."""
    fo = 2 * _M_MGO / (2 * _M_MGO + _M_SIO2) * 100
    fa = 2 * _M_FEO / (2 * _M_FEO + _M_SIO2) * 100
    return np.array([fo, 0.0]), np.array([0.0, fa])
