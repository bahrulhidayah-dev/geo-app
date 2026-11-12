"""Make the example dataset "Hydrogen practice set: 20 synthetic rocks".

Every rock (except the basalt) is a mixture of ideal minerals with KNOWN
proportions, so the answers of Tools -> Hydrogen generation are known:
the mineral modes, C, the degree of serpentinization S and the H2.
The basalt is a typical analysis (not a mixture) and must be left out by
the ultramafic screening.

Four scenarios (column Group):
  A  Serpentinization series: one harzburgite at 0, 20, 40, 60, 80, 100 %
     serpentinization, all at 280 C.
  B  Protolith types: fresh dunite, lherzolite, wehrlite, olivine
     websterite, orthopyroxenite, all at 300 C.
  C  Drill core: one partly serpentinized harzburgite (S = 0.5) at 1, 3,
     6, 9.7 and 12 km depth (temperature from 23 C + 30 C/km).
  D  Special cases at 200 C: carbonate in the LOI (CO2 column), brucite,
     measured H2O+, and a basalt.

Temperature (C) = 23 + 30 x depth (km) for every sample; Pressure (bar) =
hydrostatic at that depth (1000 kg/m3 x 9.81 m/s2 x depth).

Run from the geo-app folder:  python tools/make_hydrogen_examples.py
Writes geochem/examples/hydrogen_synthetic_20.csv and
test_data/hydrogen_synthetic_20_answers.csv (known modes, S and H2).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from geochem import hydrogen, modes  # noqa: E402

OL, OPX, CPX, SPL, SRP, BRC, MAG = ("Olivine (Fo90)", "Orthopyroxene (En90)",
                                    "Clinopyroxene (diopside)", "Spinel (MgAl2O4)",
                                    "Serpentine (Mg3Si2O5(OH)4)", "Brucite (Mg(OH)2)",
                                    "Magnetite (Fe3O4)")
MIN = [OL, OPX, CPX, SPL, SRP, BRC, MAG]
A = modes.mineral_table(MIN)                       # components x minerals, wt%
CALCITE = {"CaO": 56.03, "CO2": 43.97}             # CaCO3, wt%


def serpentinize(fresh, s):
    """Replace the fraction s of olivine + orthopyroxene by serpentine (95 %)
    and magnetite (5 %). Returns the new modes (wt%, sum unchanged)."""
    m = dict(fresh)
    reacted = s * (m.get(OL, 0) + m.get(OPX, 0))
    m[OL] = m.get(OL, 0) * (1 - s)
    m[OPX] = m.get(OPX, 0) * (1 - s)
    m[SRP] = m.get(SRP, 0) + 0.95 * reacted
    m[MAG] = m.get(MAG, 0) + 0.05 * reacted
    return m


HZB = {OL: 75, OPX: 20, CPX: 2, SPL: 3}
rows = []   # (sample, group, rock type, modes dict, T, extra)
for s in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
    name = "fresh harzburgite" if s == 0 else ("serpentinite" if s == 1
                                               else "serpentinized harzburgite")
    rows.append((f"A{int(s * 100):03d}", "A Serpentinization series",
                 name[0].upper() + name[1:], serpentinize(HZB, s), 280.0, {}))
for code, rock, m in (("B-DUN", "Dunite", {OL: 97, OPX: 1, SPL: 2}),
                      ("B-LHZ", "Lherzolite", {OL: 60, OPX: 25, CPX: 12, SPL: 3}),
                      ("B-WEH", "Wehrlite", {OL: 60, CPX: 38, SPL: 2}),
                      ("B-OWB", "Olivine websterite", {OL: 25, OPX: 40, CPX: 33, SPL: 2}),
                      ("B-OPX", "Orthopyroxenite", {OL: 5, OPX: 90, CPX: 3, SPL: 2})):
    rows.append((code, "B Protolith types", rock, m, 300.0, {}))
for depth_km in (1.0, 3.0, 6.0, 9.7, 12.0):
    rows.append((f"C-{depth_km:04.1f}km", "C Drill core", "Serpentinized harzburgite",
                 serpentinize(HZB, 0.5), 23.0 + 30.0 * depth_km, {}))
# D: special cases
rows.append(("D-CARB", "D Special cases", "Serpentinite with carbonate veins",
             serpentinize(HZB, 0.7), 200.0, {"calcite": 5.0}))
rows.append(("D-BRC", "D Special cases", "Brucite-bearing serpentinite",
             {**serpentinize({OL: 90, OPX: 5, SPL: 2, CPX: 3}, 0.8), BRC: 8.0}, 200.0,
             {"rescale": True}))
rows.append(("D-H2O+", "D Special cases", "Serpentinite (H2O+ measured)",
             serpentinize(HZB, 0.9), 200.0, {"h2o_plus": True, "loi_extra": 1.2}))
rows.append(("D-BAS", "D Special cases", "Basalt", None, 200.0, {"basalt": True}))

BASALT = {"SiO2": 49.5, "TiO2": 1.8, "Al2O3": 15.2, "FeOt": 10.4, "MgO": 7.6, "CaO": 11.0,
          "Na2O": 2.6, "K2O": 0.4, "H2O": 0.9}

out, truth = [], []
for name, group, rock, m, T, extra in rows:
    if extra.get("basalt"):
        comp = dict(BASALT)
        mm = {k: np.nan for k in MIN}
    else:
        mm = {k: float(m.get(k, 0.0)) for k in MIN}
        if extra.get("rescale"):                     # keep the sum at 100 %
            tot = sum(mm.values())
            mm = {k: 100 * v / tot for k, v in mm.items()}
        x = pd.Series(mm) / 100.0
        rock_c = A @ x
        comp = {c: float(rock_c[c]) for c in A.index}
        comp.update({"TiO2": 0.0, "Na2O": 0.0, "K2O": 0.0})
        cal = extra.get("calcite", 0.0)
        if cal:                                      # add calcite, then rescale to 100 %
            f = (100 - cal) / 100
            comp = {k: v * f for k, v in comp.items()}
            mm = {k: v * f for k, v in mm.items()}
            comp["CaO"] += cal * CALCITE["CaO"] / 100
            comp["CO2"] = cal * CALCITE["CO2"] / 100
    depth_m = (T - 23.0) / 30.0 * 1000.0
    row = {"Sample": name, "Group": group, "Rock type": rock,
           "SiO2": comp["SiO2"], "TiO2": comp["TiO2"], "Al2O3": comp["Al2O3"],
           "Fe2O3t": comp["FeOt"] / 0.8998, "MgO": comp["MgO"], "CaO": comp["CaO"],
           "Na2O": comp["Na2O"], "K2O": comp["K2O"],
           "LOI": comp["H2O"] + comp.get("CO2", 0.0) + extra.get("loi_extra", 0.0),
           "H2O+": comp["H2O"] if extra.get("h2o_plus") else np.nan,
           "CO2": comp.get("CO2", np.nan),
           "Temperature (°C)": T, "Depth (m)": depth_m,
           "Pressure (bar)": float(hydrogen.pressure_from_depth(depth_m, "hydrostatic"))}
    out.append(row)
    srp = mm[SRP]
    c_true = hydrogen.composition_correction(
        {"olivine": mm[OL] / 100, "orthopyroxene": mm[OPX] / 100,
         "clinopyroxene": mm[CPX] / 100})["C"] if not extra.get("basalt") else np.nan
    truth.append({"Sample": name, **{k.split(" (")[0]: v for k, v in mm.items()},
                  "C true": c_true, "S true (serpentine/100)": srp / 100 if pd.notna(srp) else np.nan,
                  "H2 true (mmol/kg, S x 227)": srp / 100 * 227 if pd.notna(srp) else np.nan,
                  "RH2 (mmol/kg, Eq. 3-5, no pressure)": hydrogen.rh2_rate(T)["rate_mmol_kg"]})

data = pd.DataFrame(out)
num = data.select_dtypes("number").columns
data[num] = data[num].round(3)
dst = ROOT / "geochem" / "examples" / "hydrogen_synthetic_20.csv"
data.to_csv(dst, index=False)
ans = pd.DataFrame(truth)
(ROOT / "test_data").mkdir(exist_ok=True)
ans.round(4).to_csv(ROOT / "test_data" / "hydrogen_synthetic_20_answers.csv", index=False)
if __name__ == "__main__":
    pd.set_option("display.width", 200)
    print(data.drop(columns=["Group"]).to_string(index=False))
    print()
    print(ans.round(3).to_string(index=False))
