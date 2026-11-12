"""Synthetic test for Tools -> Hydrogen generation (v0.26.0).

Idea: invent six rocks with KNOWN mineral modes, temperatures and depths.
Mix the ideal mineral compositions to get the whole-rock analysis, as a lab
would report it (Fe2O3t and LOI). Then let the app work backwards:
whole rock -> mineral modes -> C -> RH2, and compare with the known answer.

Run from the geo-app folder:  python tools/synthetic_h2_test.py
Writes test_data/synthetic_h2_samples.csv (can be opened in the app).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from geochem import hydrogen, modes  # noqa: E402

MIN = modes.DEFAULT_MINERALS
SHORT = ["Ol", "Opx", "Cpx", "Spl", "Srp", "Mag"]

# Known mineral modes (wt%) of six invented rocks
TRUE_MODES = pd.DataFrame(
    [[96, 2, 0, 2, 0, 0],      # fresh dunite
     [75, 20, 2, 3, 0, 0],     # fresh harzburgite
     [60, 25, 12, 3, 0, 0],    # fresh lherzolite
     [40, 15, 3, 2, 38, 2],    # partly serpentinised harzburgite
     [0, 2, 1, 2, 88, 7],      # fully serpentinised (serpentinite)
     [5, 50, 43, 2, 0, 0]],    # websterite (pyroxene-rich)
    index=["SYN-DUN", "SYN-HZB", "SYN-LHZ", "SYN-SHZ", "SYN-SRP", "SYN-WEB"],
    columns=MIN, dtype=float)
TEMP_C = [25.0, 150.0, 250.0, 300.0, 350.0, 420.0]   # one per rock

# 1. Whole-rock analysis = mixture of the ideal minerals
A = modes.mineral_table(MIN)                     # rows = components, cols = minerals
rock = (A @ (TRUE_MODES.T / 100.0)).T            # wt% of each component
data = pd.DataFrame({"Sample": TRUE_MODES.index, "Group": "Synthetic"})
data["SiO2"] = rock["SiO2"].values
data["Al2O3"] = rock["Al2O3"].values
data["Fe2O3t"] = (rock["FeOt"] / 0.8998).values   # as a lab reports total iron
data["MgO"] = rock["MgO"].values
data["CaO"] = rock["CaO"].values
data["LOI"] = rock["H2O"].values                   # LOI = water here
data["Temperature (C)"] = TEMP_C
data["Depth (m)"] = [(T - 23.0) / 30.0 * 1000.0 for T in TEMP_C]   # 23 C + 30 C/km
out = Path(__file__).resolve().parents[1] / "test_data" / "synthetic_h2_samples.csv"
out.parent.mkdir(exist_ok=True)
data.round(4).to_csv(out, index=False)

# 2. Expected answers, by hand from the equations of Rezaee (2025)
def expected_c(m):
    return (m.iloc[0] * 1.0 + m.iloc[1] * 0.7 + m.iloc[2] * 0.5) / 100.0

def expected_rate(T):
    if T > 400:
        return 0.0
    return max(0.43 * T - 9.33, 0.0) if T <= 315 else -1.38 * T + 571.3

# 3. What the app calculates
df = data.copy()
rocks = modes.rock_components(df)
comps = [c for c in modes.COMPONENTS if rocks[c].notna().any()]
table, _ = modes.solve_all(rocks[comps], A.loc[comps])
rows = []
for i, name in enumerate(TRUE_MODES.index):
    cm = hydrogen.c_from_modes(table.loc[i])
    r = hydrogen.rh2_rate(TEMP_C[i])["rate_mmol_kg"]
    Tz = float(hydrogen.temperature_from_depth(df.loc[i, "Depth (m)"]))
    rows.append({"Sample": name, "T (C)": TEMP_C[i],
                 "Ol found": table.loc[i].iloc[0], "Srp found": table.loc[i].iloc[4],
                 "C expected": expected_c(TRUE_MODES.loc[name]), "C app": cm["C"],
                 "RH2 expected": expected_rate(TEMP_C[i]), "RH2 app": r,
                 "T from depth": Tz})
res = pd.DataFrame(rows)
res["CxRH2 app"] = res["C app"] * res["RH2 app"]

# 4. Volumetric test: 10 km2 body, 0-3 km, 100 m steps, no pressure (Eq. 4),
# 3000 kg/m3, C of the harzburgite. Expected sum done by hand in a loop.
area, rho, c = 10e6, 3000.0, expected_c(TRUE_MODES.loc["SYN-HZB"])
exp_total = sum(2e-6 * area * 100 * rho * c * expected_rate(23 + 0.03 * (z + 50))
                for z in range(0, 3000, 100))
tab, tot = hydrogen.volumetric_by_depth(area, 0, 3000, rho, c, pressure_mode="none")

pd.set_option("display.width", 160)
print("INPUT (whole-rock analysis written to", out.name + ")")
print(data.round(2).to_string(index=False))
print("\nKNOWN MODES (wt%)")
print(TRUE_MODES.set_axis(SHORT, axis=1).to_string())
print("\nMODES FOUND BY THE APP (wt%)")
print(table.set_axis(TRUE_MODES.index).set_axis(SHORT, axis=1).round(2).to_string())
print("\nHYDROGEN RESULTS")
print(res.round(3).to_string(index=False))
print("\nVOLUMETRIC: expected GH2 = %.4e kg, app = %.4e kg" % (exp_total, tot["GH2_kg"]))

ok = (np.allclose(table.values, TRUE_MODES.values, atol=0.01)
      and np.allclose(res["C app"], res["C expected"], atol=1e-4)
      and np.allclose(res["RH2 app"], res["RH2 expected"], atol=1e-9)
      and np.allclose(res["T from depth"], res["T (C)"], atol=1e-9)
      and abs(tot["GH2_kg"] / exp_total - 1) < 1e-12)
print("\nALL CHECKS PASSED" if ok else "\nSOME CHECKS FAILED")
