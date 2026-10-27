# geochem/norms.py
# CIPW norm, ported line by line from GCDkit 6.3 (Norms/CIPW.r; Janousek et al.
# 2006, GPL), which follows Hutchison (1974, 1975). Part of GeoChem App (GPL-3.0).

import numpy as np
import pandas as pd

from .calc import FEO_PER_FE2O3
from . import iron as _iron

# Molar masses of the oxides used by the norm (g/mol)
MW = {"SiO2": 60.0843, "TiO2": 79.8658, "Al2O3": 101.9613, "Fe2O3": 159.6882,
      "FeO": 71.8444, "MnO": 70.9374, "MgO": 40.3044, "CaO": 56.0774,
      "Na2O": 61.9789, "K2O": 94.1960, "H2O": 18.0153, "CO2": 44.0098,
      "P2O5": 141.9445, "F": 18.9984, "S": 32.065}
OXIDES = ["SiO2", "TiO2", "Al2O3", "Fe2O3", "FeO", "MnO", "MgO", "CaO", "Na2O",
          "K2O", "H2O", "CO2", "P2O5", "F", "S"]

RESULT_NAMES = ["Q", "C", "Or", "Ab", "An", "Lc", "Ne", "Kp", "Nc", "Ac", "Ns",
                "Ks", "Di", "MgDi", "FeDi", "Wo", "Hy", "En", "Fs", "Ol", "Fo",
                "Fa", "Dcs", "Mt", "Il", "Hm", "Tn", "Pf", "Ru", "Ap", "Fr", "Py",
                "Cc", "Sp", "MgSp", "FeSp"]
# Normative mineral molar masses (Hutchison 1974, 1975), same order as above;
# 1 = placeholder for minerals summed from their end members
WEIGHTS = [60.08480, 101.96128, 556.66548, 524.44902, 278.21028, 436.49588,
           284.10982, 316.32628, 105.98874, 462.01034, 122.06374, 154.28020, 1,
           216.5534, 248.09, 116.16, 1, 100.39, 131.93, 1, 140.70, 203.78,
           172.24, 231.54, 151.75, 159.69, 196.06, 135.98, 79.90, 336.21, 78.08,
           119.98, 100.09, 1, 142.27, 173.81]
INTERNAL = ["qtz", "cor", "ort", "ab", "an", "lc", "ne", "kp", "nc", "ac", "ns",
            "ks", "di", "mgdi", "fedi", "wo", "hy", "en", "fs", "ol", "fo", "fa",
            "cs", "mt", "il", "hm", "tn", "pf", "ru", "ap", "fr", "pr", "cc", "sp",
            "mgsp", "fesp"]


def _norm_one(m, spinel=False, cancrinite=False):
    """CIPW norm of one sample. m: oxide moles (wt% / molar mass)."""
    si, ti, al, fe3, fe2, mn, mg, ca, na, k, h2o, co2, p, fl, s = m
    fe2 = fe2 + mn
    y = {n: 0.0 for n in INTERNAL + ["mgr", "fer", "femg"]}

    if ca >= 10 / 3 * p:
        y["ap"] = p
        ca -= y["ap"] * 10 / 3
    else:
        y["ap"] = 3 / 10 * ca
        p -= y["ap"]
        ca = 0
    if fl >= 2 / 3 * y["ap"]:
        fl -= 2 / 3 * y["ap"]
    else:
        fl = 0
    if ca >= .5 * fl:
        y["fr"] = .5 * fl
        ca -= y["fr"]
    else:
        y["fr"] = ca
        fl -= 2 * y["fr"]
        ca = 0
    if fe2 >= .5 * s:
        y["pr"] = .5 * s
        fe2 -= y["pr"]
    else:
        y["pr"] = fe2
        s -= 2 * y["pr"]
        fe2 = 0
    if cancrinite:
        y["nc"] = co2
        na -= y["nc"]
    if ca >= co2:
        y["cc"] = co2
        ca -= y["cc"]
        co2 = 0
    else:
        y["cc"] = ca
        co2 -= y["cc"]
        ca = 0
    if fe2 >= ti:
        y["il"] = ti
        fe2 -= y["il"]
        ti = 0
    else:
        y["il"] = fe2
        ti -= y["il"]
        fe2 = 0
    if al >= k:
        y["ort"] = k
        al -= y["ort"]
        si -= 6 * y["ort"]
        k = 0
    else:
        y["ort"] = al
        k -= y["ort"]
        si -= 6 * y["ort"]
        al = 0
        y["ks"] = k
        si -= y["ks"]
        k = 0
    if al >= na:
        y["ab"] = na
        al -= y["ab"]
        si -= 6 * y["ab"]
        na = 0
    else:
        y["ab"] = al
        na -= y["ab"]
        si -= 6 * y["ab"]
        al = 0
    if na >= fe3:
        y["ac"] = fe3
        na -= y["ac"]
        fe3 = 0
        y["ns"] = na
        si -= 4 * y["ac"] + y["ns"]
    else:
        y["ac"] = na
        fe3 -= y["ac"]
        na = 0
        si -= 4 * y["ac"]
    if al >= ca:
        y["an"] = ca
        al -= y["an"]
        ca = 0
        si -= 2 * y["an"]
        y["cor"] = al
        al = 0
    else:
        y["an"] = al
        ca -= y["an"]
        si -= 2 * y["an"]
        al = 0
    if ca >= ti:
        y["tn"] = ti
        ca -= y["tn"]
        si -= y["tn"]
        ti = 0
    else:
        y["tn"] = ca
        ti -= y["tn"]
        ca = 0
        y["ru"] = ti
        si -= y["tn"]
        ti = 0
    if fe3 >= fe2:
        y["mt"] = fe2
        fe3 -= y["mt"]
        fe2 = 0
        y["hm"] = fe3
        fe3 = 0
    else:
        y["mt"] = fe3
        fe2 -= y["mt"]
        fe3 = 0
    tot = fe2 + mg
    y["fer"] = fe2 / tot if tot else 0.0
    y["mgr"] = mg / tot if tot else 0.0
    y["femg"] = tot
    if spinel and si < 45 and y["femg"] <= y["cor"]:
        y["mgsp"] = y["mgr"] * y["femg"]
        y["fesp"] = y["fer"] * y["femg"]
        y["cor"] -= y["mgsp"] + y["fesp"]
        y["mgsp"] = y["mgr"] * y["cor"]
        y["fesp"] = y["fer"] * y["cor"]
        y["cor"] = 0
        y["femg"] -= y["mgsp"] + y["fesp"]
    if ca >= y["femg"]:
        y["di"] = y["femg"]
        ca -= y["femg"]
        y["wo"] = ca
        si -= 2 * y["di"] + y["wo"]
        ca = 0
    else:
        y["di"] = ca
        y["femg"] -= ca
        y["hy"] = y["femg"]
        si -= 2 * y["di"] + y["hy"]

    # silica deficiency is resolved step by step
    if si >= 0:
        y["qtz"] = si
        return _finish(y)
    y["qtz"] = 0
    d = abs(si)
    if d <= y["hy"] / 2:
        y["ol"] = d
        y["hy"] -= 2 * d
        return _finish(y)
    y["ol"] = y["hy"] / 2
    d -= y["hy"] / 2
    y["hy"] = 0
    if d <= y["tn"]:
        y["tn"] -= d
        y["pf"] = d
        return _finish(y)
    y["pf"] = y["tn"]
    d -= y["tn"]
    y["tn"] = 0
    if d <= 4 * y["ab"]:
        y["ne"] = d / 4
        y["ab"] -= d / 4
        return _finish(y)
    y["ne"] = y["ab"]
    d -= 4 * y["ab"]
    y["ab"] = 0
    if d <= 2 * y["ort"]:
        y["lc"] = d / 2
        y["ort"] -= d / 2
        return _finish(y)
    y["lc"] = y["ort"]
    d -= 2 * y["ort"]
    y["ort"] = 0
    if d < y["wo"] / 2:
        y["cs"] = d
        y["wo"] -= 2 * d
        return _finish(y)
    y["cs"] = y["wo"] / 2
    d -= y["wo"] / 2
    y["wo"] = 0
    if d <= y["di"]:
        y["cs"] += d / 2
        y["ol"] += d / 2
        y["di"] -= d
        y["kp"] = 0
        return _finish(y)
    y["cs"] += y["di"] / 2
    y["ol"] += y["di"] / 2
    d -= y["di"]
    y["di"] = 0
    y["kp"] = d / 2
    y["lc"] -= d / 2
    return _finish(y)


def _finish(y):
    y["en"] = y["mgr"] * y["hy"]
    y["fs"] = y["fer"] * y["hy"]
    y["fo"] = y["mgr"] * y["ol"]
    y["fa"] = y["fer"] * y["ol"]
    y["mgdi"] = y["mgr"] * y["di"]
    y["fedi"] = y["fer"] * y["di"]
    w = np.array([y[n] for n in INTERNAL]) * np.array(WEIGHTS)
    w[12] = w[13] + w[14]      # Di = MgDi + FeDi
    w[16] = w[17] + w[18]      # Hy = En + Fs
    w[19] = w[20] + w[21]      # Ol = Fo + Fa
    w[33] = w[34] + w[35]      # Sp = MgSp + FeSp
    parts = [i for i in range(36) if i not in (13, 14, 17, 18, 20, 21, 34, 35)]
    return np.append(w, w[parts].sum())


def iron_for_norm(df, iron=0.15):
    """FeO and Fe2O3 (wt%) for the norm, and the number of samples whose iron
    was split. `iron` is a Fe3+/Fe(total) ratio or a choice from
    iron.spec(settings) (fixed ratio, Le Maitre 1976 or Middlemost 1989)."""
    feo, fe2o3, info = _iron.split(df, iron)
    return feo, fe2o3, info["n_split"]


def cipw(df, iron=0.15, normsum=False):
    """CIPW norm (wt%) for every sample. Returns (table, number of samples
    whose iron had to be split into FeO and Fe2O3)."""
    feo, fe2o3, n_split = iron_for_norm(df, iron)
    data = pd.DataFrame(index=df.index)
    for ox in OXIDES:
        if ox == "FeO":
            data[ox] = feo
        elif ox == "Fe2O3":
            data[ox] = fe2o3
        elif ox == "H2O":
            data[ox] = df["H2O+"] if "H2O+" in df else np.nan
        else:
            data[ox] = df[ox] if ox in df else np.nan
    rows = []
    for i in data.index:
        if pd.isna(data.at[i, "SiO2"]):
            rows.append([np.nan] * 37)
            continue
        m = (data.loc[i, OXIDES] / pd.Series(MW)[OXIDES]).fillna(0).to_numpy(float)
        rows.append(_norm_one(m))
    out = pd.DataFrame(rows, index=df.index, columns=RESULT_NAMES + ["Sum"])
    if normsum:
        parts = [c for c in RESULT_NAMES if c not in
                 ("MgDi", "FeDi", "En", "Fs", "Fo", "Fa", "MgSp", "FeSp")]
        out[parts] = out[parts].div(out["Sum"], axis=0) * 100
        out["Sum"] = out[parts].sum(axis=1)
    return out, n_split


def compact(table):
    """Hide end-member and empty columns, as GCDkit does by default."""
    t = table.drop(columns=["En", "Fs", "Fo", "Fa", "MgDi", "FeDi"])
    keep = [c for c in t.columns if c == "Sum" or (t[c].fillna(0) != 0).any()]
    return t[keep]
