# tools/lee2003_vmgo.py
# Calculates the V-MgO melting curves of Lee et al. (2003) for 1.5 GPa
# fO2-buffered fractional melting of spinel peridotite and writes them as the
# geometry of the catalogue diagram "LeeVMgO". Run once by the developer:
#     python tools/lee2003_vmgo.py
# Part of GeoChem App (GPL-3.0).
#
# Source: Lee C.-T.A., Brandon A.D., Norman M. (2003) Vanadium in peridotites
# as a proxy for paleo-fO2 during partial melting: prospects, limitations,
# and implications. Geochimica et Cosmochimica Acta 67, 3045-3064.
#   eq. 1  fractional melting by small equilibrium increments:
#          Cs(j+1) = D(j+1) Cs(j) / (D (1 - dF) + dF)
#   eq. 2  D = a / (10^(b dNNO + c) + 1) for cpx, olivine and spinel;
#          D(opx) = c exp(b dNNO)            (parameters of Canil 2002)
#   eq. 3  log fO2 = A/T + B + C (P - 1)/T   (buffers of Frost 1991)
#   Table 1, 1.5 GPa (pMELTS): residue MgO and modes against F
#   Starting V = 87 ppm.

import json
import math
from pathlib import Path

import numpy as np

V0 = 87.0                                   # ppm, starting peridotite
P_BAR = 15000.0                             # 1.5 GPa
T_K = 1350.0 + 273.15                       # [App convention] temperature for dFMQ -> dNNO

# Table 1, 1.5 GPa melting (pMELTS): F (%), MgO (wt%), modes (wt%)
F = [0, 1.0, 2.4, 5.0, 9.9, 18.3, 24.9, 30.3, 37.1, 46.6]
MGO = [37.5, 37.8, 38.1, 38.7, 39.8, 41.9, 43.6, 44.6, 46.0, 48.0]
OPX = [28.1, 28.3, 28.4, 28.8, 30.2, 34.4, 35.5, 32.1, 27.0, 17.8]
CPX = [19.2, 18.9, 18.3, 17.0, 13.5, 5.0, 0, 0, 0, 0]
OL = [49.6, 49.8, 50.3, 51.4, 53.8, 58.6, 62.9, 66.5, 71.9, 81.2]
SP = [3.1, 3.0, 3.0, 2.8, 2.5, 1.9, 1.6, 1.3, 1.2, 1.0]

# eq. 2 parameters (a, b, c)
CANIL = {"cpx": (8.0, 0.31, 1.22), "ol": (0.9, 0.31, 1.53), "sp": (18.5, 0.37, 0.62)}
OPX_BC = (-0.215, 0.116)


def log_fo2(buffer, t=T_K, p=P_BAR):
    a, b, c = {"NNO": (-24930.0, 9.36, 0.046), "FMQ": (-25096.3, 8.735, 0.110)}[buffer]
    return a / t + b + c * (p - 1) / t


def dnno(dfmq):
    """Delta NNO for a given delta FMQ (eq. 3)."""
    return dfmq + log_fo2("FMQ") - log_fo2("NNO")


def partition(dfmq):
    """Mineral/melt D of V for cpx, olivine, spinel and opx."""
    n = dnno(dfmq)
    d = {m: a / (10 ** (b * n + c) + 1) for m, (a, b, c) in CANIL.items()}
    b, c = OPX_BC
    d["opx"] = c * math.exp(b * n)
    return d


def melting_curve(dfmq, step=0.1):
    """Residue MgO and V (ppm) for fractional melting at fixed fO2."""
    f = np.arange(0.0, F[-1] + 1e-9, step)            # % melt extracted
    modes = {k: np.interp(f, F, v) / 100 for k, v in
             (("opx", OPX), ("cpx", CPX), ("ol", OL), ("sp", SP))}
    mgo = np.interp(f, F, MGO)
    d = partition(dfmq)
    v = [V0]
    for j in range(1, len(f)):
        df = (f[j] - f[j - 1]) / (100 - f[j - 1])       # fraction of the residue melted
        dbulk = sum(modes[m][j] * d[m] for m in d)
        v.append(dbulk * v[-1] / (dbulk * (1 - df) + df))
    return f, mgo, np.array(v)


def main():
    lines, texts = [], []
    for k in range(-3, 3):
        f, mgo, v = melting_curve(k)
        idx = np.linspace(0, len(f) - 1, 120).astype(int)
        lines.append({"x": [round(float(x), 3) for x in mgo[idx]],
                      "y": [round(float(y), 3) for y in v[idx]],
                      "lwd": 2.0 if k == 0 else 1.0, "dash": False,
                      "role": "line" if k == 0 else "minor"})
        lab = "FMQ" if k == 0 else f"FMQ{k:+d}"
        if v[-1] > 12:                                  # reduced curves: label at the end
            lx, ly = float(mgo[-1]) + 0.15, float(v[-1])
        else:                                           # oxidised curves end near 0: label
            j = int(np.argmax(v < 12))                  # where V falls below 12 ppm
            lx, ly = float(mgo[j]) + 0.15, float(v[j]) + 1.5
        texts.append({"x": lx, "y": ly, "text": lab, "rot": 0.0,
                      "size": 0.75, "adj": 0, "role": "minor"})
    for pct in (10, 20, 30, 40):                        # melt extracted, 10 % steps
        x = float(np.interp(pct, F, MGO))
        lines.append({"x": [x, x], "y": [0.0, 100.0], "lwd": 1.0, "dash": True, "role": "minor"})
        texts.append({"x": x, "y": 97.0, "text": f"{pct}%", "rot": 0.0, "size": 0.75,
                      "adj": 0.5, "role": "minor"})
    geom = {"id": "LeeVMgO",
            "source": "Lee et al. (2003): curves calculated with tools/lee2003_vmgo.py from "
                      "their eqs. 1-3 and Table 1 (1.5 GPa); no GCDkit template",
            "panels": [{"xlim": [36.0, 50.0], "ylim": [0.0, 100.0], "log_x": False,
                        "log_y": False, "xlab": "MgO (wt%, anhydrous)", "ylab": "V (ppm)",
                        "title": "V - MgO (Lee et al. 2003)", "ternary": False,
                        "name": "V - MgO (Lee et al. 2003)", "lines": lines, "polygons": [],
                        "texts": texts, "fields": [], "points": []}]}
    out = Path(__file__).resolve().parent.parent / "geochem" / "diagrams" / "gcdkit" / "LeeVMgO.json"
    out.write_text(json.dumps(geom, indent=1), encoding="utf-8")
    print("dNNO - dFMQ at 1.5 GPa and", T_K - 273.15, "C:", round(dnno(0), 3))
    for k in range(-3, 3):
        print(f"FMQ{k:+d}: D", {m: round(x, 3) for m, x in partition(k).items()},
              "| V at F = 10, 20, 30, 46.6 %:",
              [round(float(np.interp(p, *melting_curve(k)[0:3:2])), 1) for p in (10, 20, 30, 46.6)])
    print("written", out)


if __name__ == "__main__":
    main()
