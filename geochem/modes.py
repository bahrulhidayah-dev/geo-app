# geochem/modes.py
# Mineral modes from a whole-rock analysis by least squares with the closure
# condition (mineral fractions sum to 1), after Albarede (1995), Introduction
# to Geochemical Modeling, section 5.3.1. Part of GeoChem App (GPL-3.0).
#
#   y = A x       y: whole-rock composition (m components)
#                 A: mineral compositions (m components x n minerals)
#                 x: mineral mass fractions (n)
#   unconstrained solution     x0 = (A'A)^-1 A'y
#   Lagrange multiplier        lambda = (1 - J'x0) / (J'(A'A)^-1 J)
#   constrained solution       x = x0 + lambda (A'A)^-1 J,   J = (1, ..., 1)'
# Values are divided by 100 first (wt% -> fractions), as in the book.

import numpy as np
import pandas as pd

COND_LIMIT = 300   # [App convention] above this the modes are called unstable

COMPONENTS = ["SiO2", "Al2O3", "FeOt", "MgO", "CaO", "H2O"]

# Molar masses (g/mol)
_MW = {"SiO2": 60.084, "Al2O3": 101.961, "FeO": 71.844, "MgO": 40.304, "CaO": 56.077,
       "H2O": 18.015, "Fe3O4": 231.533}


def _composition(**moles):
    """wt% of the components from moles of oxides per formula unit.
    Fe is counted as FeO (FeOt); for magnetite use Fe3O4 (given as FeOt)."""
    mass = {}
    for ox, n in moles.items():
        if ox == "Fe3O4":
            mass["FeOt"] = mass.get("FeOt", 0) + n * 3 * _MW["FeO"]
            continue
        key = "FeOt" if ox == "FeO" else ox
        mass[key] = mass.get(key, 0) + n * _MW[ox]
    total = sum(n * _MW[ox] for ox, n in moles.items())
    return {c: 100 * mass.get(c, 0.0) / total for c in COMPONENTS}


# Ideal compositions [App convention]; the user can replace them with measured
# (for example EPMA) compositions on the page. Olivine Fo90 and orthopyroxene
# En90 are typical of mantle peridotite; the hydrous phases are Mg end-members.
MINERALS = {
    "Olivine (Fo90)": _composition(MgO=1.8, FeO=0.2, SiO2=1),
    "Orthopyroxene (En90)": _composition(MgO=0.9, FeO=0.1, SiO2=1),
    "Clinopyroxene (diopside)": _composition(CaO=1, MgO=1, SiO2=2),
    "Spinel (MgAl2O4)": _composition(MgO=1, Al2O3=1),
    "Serpentine (Mg3Si2O5(OH)4)": _composition(MgO=3, SiO2=2, H2O=2),
    "Brucite (Mg(OH)2)": _composition(MgO=1, H2O=1),
    "Magnetite (Fe3O4)": _composition(Fe3O4=1),
    "Talc (Mg3Si4O10(OH)2)": _composition(MgO=3, SiO2=4, H2O=1),
    "Chlorite (clinochlore)": _composition(MgO=5, Al2O3=1, SiO2=3, H2O=4),
}
# Six minerals for the six components of a serpentinised harzburgite or
# lherzolite. Brucite is not in the default set: with olivine, orthopyroxene
# and serpentine it is nearly dependent (serpentine = 2 enstatite + brucite +
# H2O; condition number about 5000), so its mode cannot be resolved from a
# whole-rock analysis alone.
DEFAULT_MINERALS = ["Olivine (Fo90)", "Orthopyroxene (En90)", "Clinopyroxene (diopside)",
                    "Spinel (MgAl2O4)", "Serpentine (Mg3Si2O5(OH)4)", "Magnetite (Fe3O4)"]


def mineral_table(names=None):
    """Mineral compositions (rows = components, columns = minerals), wt%."""
    names = names or list(MINERALS)
    return pd.DataFrame({n: MINERALS[n] for n in names}).reindex(COMPONENTS)


def solve(y, A, closure=True, normalise=False):
    """Constrained least squares (Albarede 1995, section 5.3.1).
    y: Series (components, wt%); A: DataFrame (components x minerals, wt%).
    Components missing in y are left out. Returns a dict with x (fractions),
    x0, lambda, the fitted composition, residuals (wt%), the sum of squared
    residuals, the rank of A and a list of warnings.

    normalise: the closure condition assumes that the rock and every mineral
    add up to the same total over the components used. A real analysis does
    not (minor oxides are left out, Fe2O3 is recast as FeO), and neither does
    magnetite written as FeOt (93.1 %). With normalise=True the rock and each
    mineral are first scaled to 100 % over the components used; the fractions
    found on that basis (x'_i) are converted back to mass fractions with
    x_i = (x'_i / s_i) / sum_j (x'_j / s_j), s_i being the original sum of
    mineral i over the components used. [App convention]"""
    comps = [c for c in A.index if c in y.index and pd.notna(y[c])]
    Am = A.loc[comps].to_numpy(dtype=float) / 100
    yv = y[comps].to_numpy(dtype=float) / 100
    scale = None
    if normalise:
        scale = Am.sum(axis=0)
        scale[scale <= 0] = 1.0
        Am = Am / scale
        ysum = yv.sum()
        yv = yv / ysum
    n = Am.shape[1]
    warnings = []
    # Rank of the equations actually used: the component rows plus, with the
    # closure condition, the row of ones. When every mineral composition sums
    # to 100 %, the closure row adds no new information.
    rows = np.vstack([Am, np.ones(n)]) if closure else Am
    rank = int(np.linalg.matrix_rank(rows, tol=1e-8))
    if rank < n:
        warnings.append("The minerals cannot all be resolved with these components "
                        "(rank {r} < {n} minerals): the modes are not unique. Remove a "
                        "mineral or add a component (for example H2O or Al2O3)."
                        .format(r=rank, n=n))
    cond = float(np.linalg.cond(rows)) if rank == n else float("inf")
    if rank == n and cond > COND_LIMIT:
        warnings.append("The minerals are nearly dependent (condition number {c:.0f}): "
                        "small analytical errors change the modes a lot. Check the "
                        "uncertainties, or remove a mineral.".format(c=cond))
    AtA = Am.T @ Am
    inv = np.linalg.pinv(AtA)
    x0 = inv @ Am.T @ yv
    lam, x = 0.0, x0
    if closure:
        J = np.ones(n)
        if np.linalg.matrix_rank(AtA, tol=1e-10) == n:
            # Albarede (1995), eqs. for the Lagrange multiplier
            lam = float((1 - J @ x0) / (J @ inv @ J))
            x = x0 + lam * (inv @ J)
        else:
            # A'A is singular: solve the same problem as one bordered system
            # [A'A J; J' 0][x; mu] = [A'y; 1] (minimum-norm solution)
            K = np.block([[AtA, J[:, None]], [J[None, :], np.zeros((1, 1))]])
            sol = np.linalg.lstsq(K, np.append(Am.T @ yv, 1.0), rcond=None)[0]
            x, lam = sol[:n], float("nan")
    fit = Am @ x * 100
    res = yv * 100 - fit
    if normalise:                       # back to the units of the analysis
        fit, res = fit * ysum, res * ysum
        x0 = x0 * ysum / scale            # unconstrained: no renormalisation
        x = x / scale / (x / scale).sum()
    if (x < -0.005).any():
        warnings.append("Some fractions are negative: that mineral is probably absent or "
                        "its composition does not fit; remove it and solve again.")
    names = list(A.columns)
    return {"x": pd.Series(x, index=names), "x0": pd.Series(x0, index=names),
            "lambda": lam, "components": comps,
            "fit": pd.Series(fit, index=comps), "residual": pd.Series(res, index=comps),
            "ssr": float((res ** 2).sum()), "rank": rank, "condition": cond,
            "warnings": warnings}


def analytical_sd(y):
    """[App convention] 1-sigma analytical error of each component: 1 % relative,
    at least 0.05 wt%."""
    y = pd.Series(y, dtype=float)
    return np.maximum(0.01 * y.abs(), 0.05)


def uncertainty(y, A, sd=None, n=300, seed=0, normalise=True):
    """Standard deviation (in % mode) of each mineral fraction by Monte Carlo:
    the rock analysis is perturbed n times with normal errors (sd in wt%,
    default analytical_sd) and solved again."""
    y = pd.Series(y, dtype=float)
    sd = analytical_sd(y) if sd is None else pd.Series(sd, index=y.index)
    rng = np.random.default_rng(seed)
    runs = [solve(y + rng.normal(0, 1, len(y)) * sd.fillna(0), A,
                  normalise=normalise)["x"].to_numpy()
            for _ in range(n)]
    return pd.Series(100 * np.std(runs, axis=0), index=A.columns)


def rock_components(df):
    """Whole-rock components for the mass balance: SiO2, Al2O3, FeOt (all iron
    as FeO), MgO, CaO and H2O. H2O is taken from H2O+ when given, otherwise from
    LOI [App convention: LOI also contains CO2 and S; in serpentinites it is
    mostly H2O]. Values as measured (not anhydrous), because H2O is a component."""
    from .calc import feot
    out = pd.DataFrame(index=df.index)
    for c in ("SiO2", "Al2O3", "MgO", "CaO"):
        out[c] = df[c] if c in df else np.nan
    out["FeOt"] = feot(df)
    h2o = df["H2O+"] if "H2O+" in df else pd.Series(np.nan, index=df.index)
    if "LOI" in df:
        h2o = h2o.fillna(df["LOI"].clip(lower=0))
    out["H2O"] = h2o
    return out[COMPONENTS]


def solve_all(rocks, A, normalise=True):
    """Modes (in %) of every rock (row) with the same mineral table."""
    rows, info = {}, {}
    for idx, r in rocks.iterrows():
        need = [c for c in ("SiO2", "MgO") if c in r.index]
        if r[need].isna().any() or r.notna().sum() < 2:
            continue
        out = solve(r, A, normalise=normalise)
        rows[idx] = 100 * out["x"]
        info[idx] = {"Sum of squared residuals": out["ssr"],
                     "Components used": len(out["components"])}
    return pd.DataFrame(rows).T, pd.DataFrame(info).T
