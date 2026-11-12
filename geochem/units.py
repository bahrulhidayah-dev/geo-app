# geochem/units.py
# Unit conversions for temperature, pressure, depth and density.
# Internally the app always works in degrees Celsius, bar, metres and kg/m3;
# these functions convert user input to those units and back for display.
# All factors are exact definitions (SI and NIST), not app conventions.
# Part of GeoChem App (GPL-3.0).

import numpy as np

# ---------- temperature ----------
TEMP_UNITS = ["°C", "K", "°F"]


def temp_to_c(value, unit):
    """Temperature in `unit` -> degrees Celsius."""
    v = np.asarray(value, dtype=float)
    if unit == "K":
        return v - 273.15
    if unit == "°F":
        return (v - 32.0) * 5.0 / 9.0
    return v


def temp_from_c(value_c, unit):
    """Degrees Celsius -> temperature in `unit`."""
    v = np.asarray(value_c, dtype=float)
    if unit == "K":
        return v + 273.15
    if unit == "°F":
        return v * 9.0 / 5.0 + 32.0
    return v


def temp_step_per_c(unit):
    """Size of one degree Celsius in `unit` (for gradients and differences)."""
    return 1.8 if unit == "°F" else 1.0


# ---------- pressure ----------
# bar per unit (exact: 1 atm = 101325 Pa; 1 psi = 6894.757 Pa; 1 bar = 1e5 Pa)
PRESSURE_BAR = {"bar": 1.0, "atm": 1.01325, "MPa": 10.0, "kPa": 0.01,
                "GPa": 10000.0, "psi": 0.06894757}
PRESSURE_UNITS = list(PRESSURE_BAR)


def pressure_to_bar(value, unit):
    return np.asarray(value, dtype=float) * PRESSURE_BAR[unit]


def pressure_from_bar(value_bar, unit):
    return np.asarray(value_bar, dtype=float) / PRESSURE_BAR[unit]


# ---------- depth / length ----------
DEPTH_M = {"m": 1.0, "km": 1000.0, "ft": 0.3048}
DEPTH_UNITS = list(DEPTH_M)


def depth_to_m(value, unit):
    return np.asarray(value, dtype=float) * DEPTH_M[unit]


def depth_from_m(value_m, unit):
    return np.asarray(value_m, dtype=float) / DEPTH_M[unit]


# ---------- area ----------
AREA_M2 = {"km²": 1e6, "m²": 1.0, "ha": 1e4, "mi²": 2589988.110336}
AREA_UNITS = list(AREA_M2)


def area_to_m2(value, unit):
    return np.asarray(value, dtype=float) * AREA_M2[unit]


# ---------- density ----------
DENSITY_KGM3 = {"kg/m³": 1.0, "g/cm³": 1000.0}
DENSITY_UNITS = list(DENSITY_KGM3)


def density_to_kgm3(value, unit):
    return np.asarray(value, dtype=float) * DENSITY_KGM3[unit]


def density_from_kgm3(value, unit):
    return np.asarray(value, dtype=float) / DENSITY_KGM3[unit]


if __name__ == "__main__":
    # quick checks against textbook values
    assert abs(float(temp_from_c(100, "°F")) - 212) < 1e-9
    assert abs(float(temp_to_c(373.15, "K")) - 100) < 1e-9
    assert abs(float(pressure_to_bar(1, "atm")) - 1.01325) < 1e-12
    assert abs(float(pressure_from_bar(500, "MPa")) - 50) < 1e-12
    assert abs(float(pressure_to_bar(14.5038, "psi")) - 1.0) < 1e-4
    assert abs(float(depth_to_m(1, "ft")) - 0.3048) < 1e-12
    assert abs(float(density_to_kgm3(3.0, "g/cm³")) - 3000) < 1e-9
    print("units: all checks passed")
