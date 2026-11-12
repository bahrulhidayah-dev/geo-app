# geochem/hydrogen.py
# Natural hydrogen (H2) generation from serpentinization: rate from
# temperature and pressure, a mineral correction factor and a volumetric
# estimate for a rock body. Part of GeoChem App (GPL-3.0).
#
# Source: Rezaee R. (2025) Quantifying natural hydrogen generation rates and
# volumetric potential in onshore serpentinization. Geosciences 15, 112.
# https://doi.org/10.3390/geosciences15030112
#
# Tags used in the docstrings:
#   [Source]          taken directly from the paper
#   [App convention]  a choice made by this app, documented in docs/methods.md

import numpy as np
import pandas as pd

T_PEAK = 315.0       # C, peak of H2 generation (McCollom and Bach 2009)
T_MAX = 400.0        # C, upper stability limit of olivine with water
G = 9.81             # m/s2
WATER_DENSITY = 1000.0   # kg/m3
KG_PER_MMOL = 2e-6   # [Source] conversion used in Eq. 8 (H2 taken as 2 g/mol)


# ---------------- 1. generation rate RH2 ----------------
def rh2_rate(temp_c, pressure_bar=None):
    """Hydrogen generation rate RH2 (mmol H2 per kg of rock).

    [Source] Rezaee (2025):
      Eq. 3  RH2 = 3.102 + 0.12 T + 0.073 P      T <= 315 C (T in C, P in bar)
      Eq. 4  RH2 = 0.43 T - 9.33                 T <  315 C (no pressure term)
      Eq. 5  RH2 = -1.38 T + 571.3               315 C < T <= 400 C
      Above 400 C generation is taken as negligible.
    Eq. 3 is used when a pressure is given, otherwise Eq. 4.
    [App convention] negative results (Eq. 4 below about 22 C) are set to 0;
    below 0 C no rate is returned.
    """
    if temp_c is None or pd.isna(temp_c):
        return {"rate_mmol_kg": None, "equation": None, "note": "No temperature."}
    temp_c = float(temp_c)
    if temp_c < 0:
        return {"rate_mmol_kg": None, "equation": None,
                "note": "Temperature below 0 C: outside the model."}

    if temp_c > T_MAX:
        return {"rate_mmol_kg": 0.0, "equation": "none",
                "note": "Above 400 C: olivine stability limit, H2 generation assumed negligible."}

    if temp_c <= T_PEAK:
        if pressure_bar is not None and not pd.isna(pressure_bar):
            rate = 3.102 + (0.12 * temp_c) + (0.073 * float(pressure_bar))
            eq = "Eq. 3"
        else:
            rate = (0.43 * temp_c) - 9.33
            eq = "Eq. 4"
        note = "Valid range: 0-315 C (rising limb)."
    else:
        rate = (-1.38 * temp_c) + 571.3
        eq = "Eq. 5"
        note = "Valid range: 315-400 C (falling limb)."

    return {"rate_mmol_kg": max(rate, 0.0), "equation": eq, "note": note}


def rate_curve(temps, pressure_bar=None):
    """RH2 for an array of temperatures (for plotting)."""
    return np.array([rh2_rate(T, pressure_bar)["rate_mmol_kg"] or 0.0 for T in temps])


# ---------------- 2. mineral correction factor C ----------------
# [Source] Table 2 of Rezaee (2025). The paper states that these ranks are
# the author's own provisional judgment, not experimental values.
STABILITY_RANK = {
    "olivine": 1.0,
    "orthopyroxene": 0.7,
    "clinopyroxene": 0.5,
}


def composition_correction(fractions):
    """Weighted correction factor C from mineral mass fractions (0-1).

    [Source] C = sum(fraction x rank); minerals that do not take part in
    serpentinization (feldspar, and here also spinel, serpentine, magnetite,
    brucite, talc, chlorite) count with rank 0.
    Example from the paper: 60 % olivine + 40 % orthopyroxene -> C = 0.88.
    """
    c_value = 0.0
    total_fraction = 0.0
    for mineral, fraction in fractions.items():
        if fraction is None or pd.isna(fraction):
            continue
        rank = STABILITY_RANK.get(str(mineral).strip().lower(), 0.0)
        c_value += float(fraction) * rank
        total_fraction += float(fraction)
    return {"C": c_value, "total_fraction_used": total_fraction}


def rank_key(mineral_name):
    """Which rank a mineral name from the Mineral modes page belongs to:
    'Olivine (Fo90)' -> 'olivine'. Unknown minerals -> None (rank 0)."""
    name = str(mineral_name).strip().lower()
    for key in STABILITY_RANK:
        if name.startswith(key):
            return key
    return None


def c_from_modes(modes_pct):
    """C from a row of mineral modes in wt% (from Tools -> Mineral modes).

    [App convention] negative modes (a mineral that does not fit) are set to
    0 and modes are used as given (they already add up to about 100 %).
    Returns C and the olivine, orthopyroxene and clinopyroxene fractions.
    """
    fr = {k: 0.0 for k in STABILITY_RANK}
    for name, value in pd.Series(modes_pct, dtype=float).items():
        key = rank_key(name)
        if key is not None and not pd.isna(value):
            fr[key] += max(float(value), 0.0) / 100.0
    out = composition_correction(fr)
    return {"C": out["C"], **fr}


# ---------------- 3. temperature and pressure from depth ----------------
def temperature_from_depth(depth_m, surface_c=23.0, gradient_c_per_km=30.0):
    """[Source] T = surface temperature + gradient x depth. The paper uses
    23 C at the surface and 30 C/km."""
    return surface_c + gradient_c_per_km * np.asarray(depth_m, dtype=float) / 1000.0


PRESSURE_MODES = ["hydrostatic", "lithostatic", "none"]


def pressure_from_depth(depth_m, mode="hydrostatic", rock_density_kgm3=3000.0):
    """Pressure (bar) at a depth.

    [App convention] The paper's P is the pore pressure of water in open
    fractures but it does not say how P was obtained from depth.
      hydrostatic:  P = 1000 kg/m3 x g x z   (about 98 bar/km)
      lithostatic:  P = rock density x g x z (about 294 bar/km at 3000 kg/m3)
      none:         no pressure, so Eq. 4 is used below 315 C.
    """
    z = np.asarray(depth_m, dtype=float)
    if mode == "hydrostatic":
        return WATER_DENSITY * G * z / 1e5
    if mode == "lithostatic":
        return rock_density_kgm3 * G * z / 1e5
    return None


# ---------------- 4. volumetric estimate ----------------
def volumetric_h2(area_m2, thickness_m, rock_density_kgm3, c_value, rh2_mmol_kg,
                  reacted_fraction=1.0):
    """Five-stage volumetric estimate of the H2 generated (GH2).

    [Source] Rezaee (2025), Eqs. 6-8:
      1. GRV (m3) = area x thickness
      2. GRM (kg) = GRV x rock density
      3. C        = composition correction factor
      4. RH2      = generation rate, mmol/kg
      5. GH2 (kg) = 2e-6 x GRM x C x RH2
    reacted_fraction: share of the rock that actually serpentinized (the
    paper uses 0.01 for the Giles Complex). 1.0 = the whole body.
    """
    grv_m3 = area_m2 * thickness_m
    grm_kg = grv_m3 * rock_density_kgm3
    gh2_kg = KG_PER_MMOL * grm_kg * c_value * rh2_mmol_kg * reacted_fraction
    return {"GRV_m3": grv_m3, "GRM_kg": grm_kg, "GH2_kg": gh2_kg}


def volumetric_by_depth(area_m2, top_m, base_m, rock_density_kgm3, c_value,
                        step_m=100.0, reacted_fraction=1.0, surface_c=23.0,
                        gradient_c_per_km=30.0, pressure_mode="hydrostatic"):
    """Volumetric GH2 of a body divided into depth intervals (as the paper
    does for the Giles Complex: 100 m steps, constant area from top to base).

    Each interval: mid depth -> T and P -> RH2 (Eqs. 3-5) -> GH2 of that
    interval's own mass (area x interval thickness x density). The total is
    the sum over intervals.
    Returns (table, totals).
    """
    if base_m <= top_m or step_m <= 0 or area_m2 <= 0:
        return pd.DataFrame(), {"GRV_m3": 0.0, "GRM_kg": 0.0, "GH2_kg": 0.0}
    tops = np.arange(top_m, base_m, step_m)
    bases = np.minimum(tops + step_m, base_m)
    mids = (tops + bases) / 2
    temps = temperature_from_depth(mids, surface_c, gradient_c_per_km)
    pres = pressure_from_depth(mids, pressure_mode, rock_density_kgm3)
    rows = []
    for i in range(len(tops)):
        p = None if pres is None else float(pres[i])
        r = rh2_rate(float(temps[i]), p)
        rate = r["rate_mmol_kg"] or 0.0
        v = volumetric_h2(area_m2, bases[i] - tops[i], rock_density_kgm3, c_value, rate,
                          reacted_fraction)
        rows.append({"Top (m)": tops[i], "Base (m)": bases[i], "Mid depth (m)": mids[i],
                     "T (C)": temps[i], "P (bar)": p, "Equation": r["equation"],
                     "RH2 (mmol/kg)": rate, "GRM (kg)": v["GRM_kg"], "GH2 (kg)": v["GH2_kg"]})
    table = pd.DataFrame(rows)
    totals = {"GRV_m3": area_m2 * (base_m - top_m),
              "GRM_kg": float(table["GRM (kg)"].sum()),
              "GH2_kg": float(table["GH2 (kg)"].sum())}
    return table, totals


def h2_units(gh2_kg):
    """GH2 in other units. mol uses the true molar mass of H2 (2.016 g/mol);
    the volume is at 0 C and 1 atm (22.414 L/mol)."""
    mol = gh2_kg / 0.002016
    return {"kg": gh2_kg, "t": gh2_kg / 1000.0, "Mt": gh2_kg / 1e9,
            "mol": mol, "m3_STP": mol * 0.022414}


if __name__ == "__main__":
    print(rh2_rate(300, 500))   # Eq. 3 -> 75.602
    print(rh2_rate(300))        # Eq. 4 -> 119.67
    print(rh2_rate(350))        # Eq. 5 -> 88.3
    print(rh2_rate(450))        # 0
    print(composition_correction({"olivine": 0.6, "orthopyroxene": 0.4}))   # C = 0.88
    print(volumetric_h2(1_000_000, 100, 3200, 0.88, 100))                   # GH2 = 5.632e7 kg
