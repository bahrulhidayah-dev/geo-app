# Tutorial: hydrogen generation

This tutorial takes you through **Tools → Hydrogen generation** from the
first step to the final numbers. You will:

1. prepare a data file;
2. choose your units;
3. calculate the H₂ generation rate for one condition;
4. calculate it for every sample, and edit the inputs in the table;
5. estimate the total H₂ of a rock body;
6. estimate how much H₂ your samples have already made;
7. read, check and report the results.

You can follow every step with the practice dataset **Hydrogen tutorial:
synthetic peridotites** (left panel → *Example datasets*). Its six rocks
were made by mixing ideal minerals in known proportions, so every expected
result in this tutorial is known exactly. Your screen should show the same
numbers. The dataset is synthetic teaching data, not real analyses.

Time needed: about 30 minutes. The scientific basis of every formula is in
**Scientific methods**, sections 8c and 8d.

## 1. What the page answers

The page answers two different questions. Keep them apart when you report
results.

| Question | Tabs | Method | Needs |
|---|---|---|---|
| How fast **could** this rock make H₂ under given conditions? | Rate (one condition), Per sample, Rock body | Empirical rate RH2 from temperature and pressure (Rezaee 2025, Eqs. 3–5), scaled by a mineral factor C (Table 2) | Temperature (or depth), optionally pressure; olivine and pyroxene contents (typed, or from the whole-rock analysis) |
| How much H₂ **has** this rock already made? | Already generated (serpentinization degree) | Degree of serpentinization S × H₂ yield of complete serpentinization (Liu et al. 2023) | Whole-rock analysis with LOI (or H2O+); total iron is enough |

Some background, in plain words:

- **Serpentinization** is the reaction of olivine and pyroxene with water
  below about 400 °C. Iron in these minerals is oxidised (Fe²⁺ → Fe³⁺ in
  magnetite and serpentine), and the water gives up hydrogen:
  2FeO + H₂O → Fe₂O₃ + H₂.
- **RH2** (mmol H₂ per kg of rock) rises with temperature to a peak near
  315 °C and falls to zero at 400 °C.
- **C** (0 to 1) says how much of the rock can still react: olivine counts
  fully (1.0), orthopyroxene 0.7, clinopyroxene 0.5, other minerals 0.
- **S** (0 to 1) is the share of the rock that has already turned into
  serpentine.

All results are estimates. The rate equations come from laboratory
experiments on powdered rock; natural rocks react more slowly. Report them
as an order of magnitude, with their assumptions.

## 2. Prepare your data

### Required and useful columns

The first column must be the **sample name**. Oxides are in **wt%**.

| Column | Needed for | Notes |
|---|---|---|
| SiO2, MgO | Per sample, Already generated | Always needed for the mineral modes |
| Al2O3, CaO | Per sample, Already generated | Recommended: they separate spinel and clinopyroxene |
| Total iron (Fe2O3t, FeOt) or FeO + Fe2O3 | Per sample, Already generated | Total iron from XRF is enough |
| LOI | Already generated | Used as water when H2O+ is missing |
| H2O+ | Already generated (better) | Used before LOI |
| CO2 | Already generated (better) | Water = LOI − CO2 when H2O+ is missing |
| Rock type or Group | All | Words such as serpentinite, harzburgite, dunite, pyroxenite help the ultramafic screening and the notes |
| Temperature (°C) | Per sample (optional) | One temperature per sample, for example from a geothermometer |
| Depth (m) | Per sample (optional) | Converted to temperature with the geothermal gradient of the first tab |
| Pressure (bar) | Per sample (optional) | Fluid pressure per sample; used up to 315 °C |

The app finds the temperature, depth and pressure columns by their names:
the name must contain *temp*, *depth* or *press* (or a unit in brackets such
as `(°C)`, `(m)`, `(bar)`, `(MPa)`). The values are read in the units you
choose on the page (section 3), so a column named `Pressure (MPa)` should be
read with the pressure unit set to MPa.

### A good file layout

| Sample | Rock type | SiO2 | Al2O3 | Fe2O3t | MgO | CaO | LOI | Temperature (°C) | Depth (m) | Pressure (bar) |
|---|---|---|---|---|---|---|---|---|---|---|
| H2-SHZ | Serpentinized harzburgite | 43.20 | 1.43 | 7.57 | 42.70 | 0.78 | 4.94 | 300 | 9233 | 906 |

This is the fourth row of the practice dataset.

### Check before you start

- **Totals.** Oxide totals including LOI should be about 98–101 wt%.
  Check them on the Data page.
- **LOI.** LOI also contains CO2 and S. If your rocks have carbonate
  veins, add a CO2 column (or H2O+), or correct the water later in the
  table (section 7).
- **Ultramafic samples.** The Already generated tab uses only ultramafic
  samples (anhydrous MgO ≥ 30 wt% in Settings, or an ultramafic word in Rock
  type or Group). You can include or exclude samples by hand later.
- **No FeO analysis?** That is fine. The app never splits total iron into
  FeO and Fe2O3 to calculate H₂: the answer would only repeat the chosen
  split.

### Load the file

Left panel → **Data file** → upload your CSV or Excel file, then check the
**Data** page: the oxides should be listed under *Recognised columns*. To
follow this tutorial, load **Example datasets → Hydrogen tutorial:
synthetic peridotites** instead.

## 3. Choose your units

Open **Tools → Hydrogen generation**. The **Units** box at the top applies
to every input, table, plot and download on the page:

| Quantity | Choices |
|---|---|
| Temperature | °C, K, °F |
| Pressure | bar, atm, MPa, kPa, GPa, psi |
| Depth | m, km, ft |
| Density | kg/m³, g/cm³ |

The area unit (km², m², ha, mi²) is on the Rock body tab.

When you change a unit, the values you typed are **converted, not reset**.
Try it: with 250 °C on the first tab, switch to K. The box shows 523.15 K
and the rate stays 98.2 mmol/kg. Switch to °F: 482 °F, still 98.2.

Internally the app always calculates in °C, bar, m and kg/m³, because the
equations of Rezaee (2025) are written in those units. The conversion
factors are exact definitions (for example 1 atm = 1.01325 bar,
1 MPa = 10 bar, 1 ft = 0.3048 m).

## 4. Step 1: the rate for one condition

Tab **Rate (one condition)**. It works without a data file.

1. **Temperature from:** *Enter the temperature* (type it), or *Depth and
   geothermal gradient* (depth, surface temperature and gradient; the app
   calculates T = surface T + gradient × depth).
2. **Pressure:** *No pressure* uses Eq. 4 (temperature only). *Enter the
   pressure* uses Eq. 3. With depth you can also choose *Hydrostatic* (water
   column, about 98 bar/km) or *Lithostatic* (rock column, about 294 bar/km
   at 3000 kg/m³). Pressure only matters up to 315 °C.
3. **Minerals of the rock:** olivine, orthopyroxene and clinopyroxene in
   wt%. Other minerals do not react in this method.

**Try it and compare:**

| Input | Expected result |
|---|---|
| 250 °C, no pressure, 100 % olivine | RH2 = 98.2 mmol/kg (Eq. 4), C = 1.00, C × RH2 = 98.2 |
| 300 °C, 500 bar (or 50 MPa), 100 % olivine | RH2 = 75.6 mmol/kg (Eq. 3) |
| 300 °C, no pressure, 60 % olivine + 40 % orthopyroxene | RH2 = 119.7, C = 0.88, C × RH2 = 105.3 |
| 450 °C | RH2 = 0 (olivine is stable with water above 400 °C) |
| Depth 7.5 km, 23 °C + 30 °C/km, hydrostatic | T = 248 °C, P = 736 bar, RH2 = 86.6 |

The plot shows the rate curve, the 315 °C peak and the 400 °C limit, with
your condition as a green point.

## 5. Step 2: every sample, with editable inputs

Tab **Per sample**. Load the practice dataset first.

1. **Temperature of each sample:** *Same as the first tab*, a temperature
   column (*Temperature (°C)*), or a depth column (*Depth (m)*, converted with
   the surface temperature and gradient of the first tab).
2. **Pressure of each sample:** *Same as the first tab*, *No pressure*, a
   pressure column, or *Hydrostatic from the depth column*.
3. The **Inputs (editable)** table shows, for every sample, the
   temperature, the pressure and the olivine, orthopyroxene and
   clinopyroxene contents. The minerals come from the mineral modes (least
   squares, Tools → Mineral modes).
4. The **Results** table shows C, the equation used, RH2 and C × RH2.

**Expected results** with *Column: Temperature (°C)* and *No pressure*:

| Sample | C | Equation | RH2 (mmol/kg) | C × RH2 |
|---|---|---|---|---|
| H2-DUN | 0.97 | Eq. 4 | 1.42 | 1.38 |
| H2-HZB | 0.90 | Eq. 4 | 55.17 | 49.65 |
| H2-LHZ | 0.84 | Eq. 4 | 98.17 | 81.97 |
| H2-SHZ | 0.52 | Eq. 4 | 119.67 | 62.23 |
| H2-SRP | 0.02 | Eq. 5 | 88.30 | 1.68 |
| H2-WEB | 0.62 | none (420 °C) | 0.00 | 0.00 |

With the pressure column (*Column: Pressure (bar)*) Eq. 3 is used below
315 °C: H2-HZB gives 51.42 and H2-SHZ 105.22 mmol/kg. Above 315 °C nothing
changes, because Eq. 5 has no pressure term.

### Edit the inputs

Click any white cell of the Inputs table and type a new value; the results
update at once.

- **Change a temperature or pressure** for one sample, for example a
  geothermometer result. Clear the pressure cell to use Eq. 4.
- **Type the protolith minerals.** H2-SRP is a serpentinite: almost no
  olivine is left, so C = 0.02. To see what the original harzburgite could
  make, type olivine 80, orthopyroxene 15, clinopyroxene 3: C becomes 0.92.
- **Undo my edits** puts back the start values. Changing the selections
  above or a unit also starts the table again from the new values.
- The **Check** column warns when olivine + orthopyroxene +
  clinopyroxene exceed 100 %.

The CSV download contains your edited inputs and the results.

## 6. Step 3: the total for a rock body

Tab **Rock body (volumetric)**. This is the five-step method of Rezaee
(2025): rock volume → rock mass → correction factor → rate → total H₂.

1. **Area** of the ultramafic body (choose the area unit), **top depth**
   and **base depth**, and the **depth step** (default 100 m).
2. **Rock density** (ultramafic rocks: about 2900–3300 kg/m³, or
   2.9–3.3 g/cm³).
3. **Surface temperature** and **gradient**, and the **pressure** model.
4. **Correction factor C** (the default is the C of the first tab) and the
   **fraction that reacted** (1.0 = the whole body).

The body is cut into depth intervals. Each interval gets its own
temperature, pressure and rate, and its own mass; the totals are added.

**Expected results:** area 10 km², top 0, base 3 km, step 100 m,
3000 kg/m³, 23 °C + 30 °C/km, *No pressure*, C = 0.90 (the harzburgite),
fraction 1.0:

| Result | Value |
|---|---|
| Rock volume GRV | 30 km³ |
| Rock mass GRM | 9 × 10¹³ kg |
| H₂ generated GH2 | 3.23 × 10⁹ kg = 3.23 Mt |
| In mol | 1.6 × 10¹² mol |
| As gas at 0 °C and 1 atm | 3.59 × 10¹⁰ m³ |

With a fraction of 0.01 the total is 3.23 × 10⁷ kg.

The depth plot shows the rate in every interval and the depths of 315 °C
and 400 °C. The interval table (CSV) lists depth, temperature, pressure,
rate, mass and H₂ of each interval in your units.

**Important:** these totals are upper limits. Real bodies react only in
part (water supply, fractures, grain size). Also note that the worked
Giles Complex example of Rezaee (2025) could not be reproduced exactly
(Scientific methods, section 10): compare your totals with the paper only
after reading that note.

## 7. Step 4: H₂ already generated

Tab **Already generated (serpentinization degree)**. This tab uses the
chemistry of your samples, not a temperature.

1. **Degree of serpentinization from:** *Water* (H2O ÷ 13 wt%, the water
   of pure serpentine) or *Serpentine mode* (Tools → Mineral modes). The
   results table shows both, so you can compare them.
2. **H₂ yield of complete serpentinization:** 227 mmol/kg (Liu et al.
   2023), with a **low** of 150 and a **high** of 300 mmol/kg. Keep the
   central value between the low and the high.
3. The **Inputs (editable)** table: tick or untick **Include** to choose
   the samples (ticked at the start: ultramafic by the screening), and type
   a corrected **H2O (wt%)** if you know better than the LOI.
4. The results: S, H₂ with its low–high range, a bar chart, and notes.

**Expected results** with the practice dataset (S from water):

| Sample | S | H₂ (mmol/kg) | Range | Note |
|---|---|---|---|---|
| H2-DUN, H2-HZB, H2-LHZ | 0.00 | 0 | 0 | fresh rock |
| H2-SHZ | 0.38 | 86.3 | 57–114 | |
| H2-SRP | 0.88 | 199.8 | 132–264 | |
| H2-WEB | 0.00 | 0 | 0 | pyroxenite: expect less |

S from the mode gives the same values here, because in these rocks
serpentine is the only hydrous mineral.

**Edit and see:** type 9.0 as the H2O of H2-SRP: S becomes 0.69 and H₂
157 mmol/kg; the water source changes to *edited*.

The notes warn when:

- a sample is a pyroxenite (the yield is for olivine-rich rock);
- the water is above that of pure serpentine (brucite or other hydrous
  minerals?);
- S from water and S from the mode differ by more than 0.15;
- a sample uses LOI as water (LOI may contain CO2).

## 8. Read, check and report the results

### Read

- **RH2 and C × RH2** (rate tabs): what the rock *could* make per kg under
  the chosen conditions. A serpentinite has a small C: most of its potential
  is already used.
- **GH2** (rock body): the same rate summed over a body: a potential, not
  a measured amount.
- **H₂ already generated** (last tab): what the rock *has* made per kg,
  from its water. It is not the H₂ still in the rock; most of it left long
  ago or became methane.

### Check

- Do the two S values (water and mode) agree? If not, look for brucite,
  carbonate or chlorite.
- Are the minerals of the Per sample tab sensible? Compare them with
  petrography or XRD.
- Is the temperature realistic for your setting?
- Run the practice dataset once after an app update: the numbers of this
  tutorial must not change.

### Report

Download the tables (CSV) and the plots (PNG, SVG or PDF). In your
methods section, give:

- the method and source: "H₂ generation rates were calculated with the
  empirical equations of Rezaee (2025), the degree-of-serpentinization
  estimate with the yield of Liu et al. (2023), using GeoChem App
  (version …)";
- your choices: temperature source, pressure model, units, yield and its
  range, how water was obtained, which samples were included;
- that the results are order-of-magnitude estimates.

References:

- Rezaee R. (2025) Geosciences 15, 112. doi:10.3390/geosciences15030112
- Liu Z. et al. (2023) Geology 51, 284–289. doi:10.1130/G50722.1
- Klein F., Bach W., McCollom T.M. (2013) Lithos 178, 55–69.

## 9. Common problems

| Problem | Cause and solution |
|---|---|
| "This diagram needs these columns: SiO2, MgO …" | The oxides were not recognised. Check the column names on the Data page (Column setup). |
| No temperature column in the list | The column name must contain *temp*, *depth* or a unit such as `(°C)` or `(m)`. Rename it in your file. |
| All samples get the same temperature | *Temperature of each sample* is set to *Same as the first tab*. |
| Pressure has no effect | Pressure only enters Eq. 3, below 315 °C; or *No pressure* is selected. |
| RH2 = 0 | Temperature above 400 °C (olivine stable), or below about 22 °C with Eq. 4. |
| C is very small | The rock is already serpentinized. Type the protolith minerals to see its original potential. |
| "minerals > 100 %" | The modes of that sample do not fit well (a negative mode was set to 0). Check the sample on Tools → Mineral modes, or type the minerals. |
| Already generated: no samples included | No sample is ultramafic by the screening. Tick *Include*, or check the threshold in Settings. |
| S from water and from mode disagree | Other hydrous minerals or carbonate. Add H2O+ or CO2, or type the corrected water. |
| My edits disappeared | Changing a selection or a unit starts the table again from the new values. Make your choices first, then edit. |
| S looks too high for a rock with brucite | Brucite water looks like serpentine water in a whole-rock analysis; the app cannot see it (chapter 11, D-BRC). Check with XRD or thin sections and type the corrected water. |
| "not ultramafic: C not meaningful" | The method is for ultramafic rocks. Leave the sample out of your interpretation. |

## 10. Checklist

- [ ] Sample name in the first column; oxides in wt%; totals 98–101 %.
- [ ] LOI, and H2O+ or CO2 if available.
- [ ] Temperature, depth or pressure columns named clearly, with units.
- [ ] Units chosen on the page match the units of your columns.
- [ ] Rate tabs: temperature source and pressure model chosen and noted.
- [ ] Already generated: samples included checked; water source checked.
- [ ] Tables and plots downloaded; app version and choices written down.

## 11. Practice set: 20 synthetic rocks

For more practice, load **Example datasets → Hydrogen practice set: 20
synthetic rocks**. The rocks were mixed from ideal minerals with known
proportions (except the basalt), so the right answers are known. Each
group teaches one thing. All values below were checked in the app.

Every sample has *Temperature (°C)*, *Depth (m)* (23 °C + 30 °C/km) and
*Pressure (bar)* (hydrostatic) columns. On the Per sample tab choose
*Column: Temperature (°C)* and *Column: Pressure (bar)*.

### Group A: serpentinization series (280 °C)

One harzburgite (olivine 75, orthopyroxene 20, clinopyroxene 2, spinel 3
wt%) at 0, 20, 40, 60, 80 and 100 % serpentinization. All six have the same
temperature and pressure, so the same rate RH2 = 98.05 mmol/kg (Eq. 3,
840 bar). What changes is the rock:

| Sample | Serpentine (known, %) | C | C × RH2 | S | H₂ already generated (mmol/kg) |
|---|---|---|---|---|---|
| A000 | 0 | 0.90 | 88.3 | 0.00 | 0 |
| A020 | 18.1 | 0.72 | 70.8 | 0.18 | 41.0 (27–54) |
| A040 | 36.1 | 0.54 | 53.3 | 0.36 | 82.0 (54–108) |
| A060 | 54.2 | 0.37 | 35.9 | 0.54 | 123.0 (81–162) |
| A080 | 72.2 | 0.19 | 18.4 | 0.72 | 163.9 (108–217) |
| A100 | 90.3 | 0.01 | 1.0 | 0.90 | 204.9 (135–271) |

**Lesson:** the two halves of the page mirror each other. As the rock
serpentinizes, the H₂ it *has made* rises and the H₂ it *could still make*
(C × RH2) falls.

### Group B: protolith types (300 °C, RH2 = 105.22 with 906 bar)

| Sample | Rock | Olivine / Opx / Cpx (%) | C | C × RH2 |
|---|---|---|---|---|
| B-DUN | Dunite | 97 / 1 / 0 | 0.98 | 102.8 |
| B-LHZ | Lherzolite | 60 / 25 / 12 | 0.84 | 87.9 |
| B-WEH | Wehrlite | 60 / 0 / 38 | 0.79 | 83.1 |
| B-OWB | Olivine websterite | 25 / 40 / 33 | 0.70 | 73.1 |
| B-OPX | Orthopyroxenite | 5 / 90 / 3 | 0.70 | 73.1 |

All are fresh (S = 0). **Lesson:** olivine-rich rocks have the highest
potential. The two pyroxene-rich rocks get the note *pyroxenite: yield is
for peridotite* on the Already generated tab, because pyroxenites make less
H₂ (Klein et al. 2013).

### Group C: drill core (same rock, S = 0.45)

| Sample | Depth | T (°C) | Equation | RH2 | C × RH2 |
|---|---|---|---|---|---|
| C-01.0km | 1 km | 53 | Eq. 3 | 16.6 | 7.6 |
| C-03.0km | 3 km | 113 | Eq. 3 | 38.2 | 17.4 |
| C-06.0km | 6 km | 203 | Eq. 3 | 70.4 | 32.1 |
| C-09.7km | 9.7 km | 314 | Eq. 3 | 110.3 | 50.2 |
| C-12.0km | 12 km | 383 | Eq. 5 | 42.8 | 19.5 |

H₂ already generated is the same for all five (102.4 mmol/kg), because
the rock is the same. **Lesson:** the rate depends on temperature, with a
peak near 315 °C; the H₂ already made depends only on the rock. Try the
*Column: Depth (m)* option too: the results are the same.

### Group D: special cases (200 °C)

| Sample | What is special | What the app shows | Known answer |
|---|---|---|---|
| D-CARB | 5 % calcite; LOI includes 2.2 wt% CO2 (CO2 column given) | Water = LOI − CO2; S = 0.60; note: S from water and from the mode differ | S = 0.60 |
| D-BRC | 7.4 % brucite | S = 0.84, no warning | S = 0.67 |
| D-H2O+ | H2O+ measured (LOI is 1.2 wt% higher) | Water from H2O+; S = 0.81 | S = 0.81 |
| D-BAS | A basalt | Left out (not ultramafic); Per sample: "C not meaningful" | — |

**Lessons:**

- Give a **CO2** or **H2O+** column when you have one: the app then uses the
  right water (D-CARB, D-H2O+). Without the CO2 column D-CARB would give
  S = 0.77.
- **Brucite cannot be seen in a whole-rock analysis.** Its water looks
  like serpentine water, so S is 26 % too high here (D-BRC), and the app
  cannot warn you. Check brucite with XRD or thin sections, and type the
  corrected water in the table.
- The method is for ultramafic rocks only (D-BAS).
