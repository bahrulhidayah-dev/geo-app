# geochem/masschange.py
# Mass change during alteration: isocon analysis (Grant 1986, 2005), the
# equivalent enrichment-factor form of MacLean and Barrett (1993) and the
# immobility test. Used for serpentinization (Paulick et al. 2006) and any
# other alteration. Part of GeoChem App (GPL-3.0).
#
# Notation (Grant 2005): C^O original (least-altered) composition, C^A altered
# composition, M^O and M^A the equivalent masses before and after alteration.
#   isocon            C^A = (M^O / M^A) C^O          (immobile species)
#   isocon slope      s = M^O / M^A = mean of C^A_i / C^O_i over the chosen
#                     immobile species (Grant 2005, Table 1)
#   gain or loss      dC_i / C^O_i = (M^A / M^O) (C^A_i / C^O_i) - 1
#                                  = (C^A_i / C^O_i) / s - 1
#   mass change       dM / M^O = 1 / s - 1
# MacLean and Barrett (1993) write the same with an enrichment factor
# EF = C^O_imm / C^A_imm = 1 / s: reconstructed composition RC = EF C^A and
# mass change of each component dX = RC - C^O (g per 100 g of precursor).

import re

import numpy as np
import pandas as pd


def ratios(c_o, c_a):
    """C^A / C^O for every species present in both (zero or missing C^O left out)."""
    c_o, c_a = pd.Series(c_o, dtype=float), pd.Series(c_a, dtype=float)
    common = [k for k in c_o.index if k in c_a.index]
    o, a = c_o[common], c_a[common]
    ok = o.notna() & a.notna() & (o > 0)
    return (a[ok] / o[ok]).rename("CA/CO")


def isocon_slope(c_o, c_a, immobile):
    """Slope of the isocon: the mean C^A/C^O of the immobile species
    (Grant 2005). Scale-independent. Returns (slope, used species)."""
    r = ratios(c_o, c_a)
    used = [k for k in immobile if k in r.index]
    if not used:
        raise ValueError("None of the chosen immobile species has data in both compositions.")
    return float(r[used].mean()), used


def regression_slope(c_o, c_a, immobile):
    """Least-squares slope through the origin of C^A on C^O for the immobile
    species (for comparison; it depends on the units, Grant 2005)."""
    o = pd.Series(c_o, dtype=float)[immobile]
    a = pd.Series(c_a, dtype=float)[immobile]
    ok = o.notna() & a.notna()
    o, a = o[ok], a[ok]
    return float((o * a).sum() / (o * o).sum())


def gains(c_o, c_a, slope):
    """Table of gains and losses (Grant 2005, Table 1, panel A):
    C^O, C^A, C^A/C^O, dC/C^O and dC (in the unit of each species)."""
    r = ratios(c_o, c_a)
    o = pd.Series(c_o, dtype=float)[r.index]
    a = pd.Series(c_a, dtype=float)[r.index]
    rel = r / slope - 1
    return pd.DataFrame({"CO": o, "CA": a, "CA/CO": r, "dC/CO": rel, "dC": rel * o})


def mass_change_percent(slope):
    """Overall mass change relative to the original mass, in %."""
    return 100.0 * (1.0 / slope - 1.0)


def mass_change_table(df, c_o, species, immobile):
    """Isocon slope, mass change and dC of every species for every sample
    (row) of df, against one original composition c_o."""
    rows = {}
    for idx, row in df.iterrows():
        try:
            s, _ = isocon_slope(c_o, row[species], immobile)
        except ValueError:
            continue
        g = gains(c_o, row[species], s)
        out = {"Isocon slope": s, "Mass change (%)": mass_change_percent(s)}
        out.update({f"d{k}": v for k, v in g["dC"].items()})
        rows[idx] = out
    return pd.DataFrame.from_dict(rows, orient="index")


def immobility_test(df, reference, species):
    """Immobility test (MacLean and Barrett 1993): each species against a
    reference species within one precursor unit. Immobile pairs form a
    straight line through the origin with r of about 0.90-0.99.
    Returns r, the slope through the origin, the intercept of an ordinary
    least-squares line (as % of the mean of the species) and n."""
    x = df[reference].astype(float)
    out = {}
    for sp in species:
        if sp == reference or sp not in df:
            continue
        y = df[sp].astype(float)
        ok = x.notna() & y.notna()
        n = int(ok.sum())
        if n < 3:
            out[sp] = {"r": np.nan, "Slope through origin": np.nan,
                       "Intercept (% of mean)": np.nan, "n": n}
            continue
        xx, yy = x[ok].to_numpy(), y[ok].to_numpy()
        r = float(np.corrcoef(xx, yy)[0, 1]) if xx.std() > 0 and yy.std() > 0 else np.nan
        slope0 = float((xx * yy).sum() / (xx * xx).sum())
        b, a = np.polyfit(xx, yy, 1)
        out[sp] = {"r": r, "Slope through origin": slope0,
                   "Intercept (% of mean)": 100 * a / yy.mean() if yy.mean() else np.nan,
                   "n": n}
    return pd.DataFrame.from_dict(out, orient="index")


def is_oxide(name):
    """Oxides and volatiles (wt%) as opposed to trace elements (ppm)."""
    return bool(re.search(r"O\d*t?$", str(name))) or str(name) in ("LOI", "H2O+", "H2O-")


def display_scale(c_o, top=40.0):
    """Scale factors that spread the species evenly on an isocon diagram, as
    in Grant (2005, Table 1, panel C): oxides first, then trace elements,
    each group sorted by C^O, get evenly spaced plotting values from `top`
    down. Scaling does not change the isocon slope or any gain or loss."""
    o = pd.Series(c_o, dtype=float).dropna()
    o = o[o > 0]
    ox = o[[is_oxide(k) for k in o.index]].sort_values(ascending=False)
    tr = o[[not is_oxide(k) for k in o.index]].sort_values(ascending=False)
    order = pd.concat([ox, tr])
    n = len(order)
    if not n:
        return pd.Series(dtype=float)
    targets = np.linspace(top, top / n, n)
    return pd.Series(targets / order.to_numpy(), index=order.index)
