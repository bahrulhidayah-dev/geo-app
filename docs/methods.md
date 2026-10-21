# Scientific methods and transparency

This document explains how GeoChem App screens, calculates and plots your
data, step by step, so that every result can be checked and reproduced. It
is written for users who want to cite the app in a thesis or paper, and for
reviewers.

Every rule is marked with its origin:

- **[Source]**: taken from a published paper or book (reference given;
  full list in the last chapter).
- **[Janoušek et al. 2006]**: taken unchanged from the open-source
  implementation published by Janoušek et al. (2006).
- **[App convention]**: a practical choice made in GeoChem App that is
  **not** prescribed by a paper. These choices are listed together in
  chapter 9 so that you can report them or change them.

A source cited "as cited in" another work was not read directly. The rule
was taken from the work that cites it.

## 1. From the file to clean numbers

1. **Reading.** CSV or Excel (`.xlsx`). The user can choose the row that
   holds the column names (Data → Column setup).
2. **Text in number columns.** A column is read as numbers when at least
   half of its cells are numbers. [App convention]
   - Cells such as `<0.01`, `bdl`, `b.d.l.`, `n.d.`, `-` become **missing**
     (NaN), never zero. Missing values are left out of every calculation that
     needs them.
   - Decimal commas (`0,52`) are read as decimal points.
   - Every change is listed in Data → Data check.
   - Some programs replace "<x" by half the detection limit. GeoChem App
     does not do this.
3. **Rows without numbers** (units rows, empty rows) are removed and
   reported.
4. **Column names.** Common lab spellings are recognised: `SiO2 (wt%)` →
   SiO2; `Fe2O3T`, `Fe2O3*`, `T-Fe2O3` → Fe2O3t (total iron as Fe2O3);
   `FeO*` → FeOt; `H2O+` → H2O+; `CO2` → CO2; element symbols → ppm.
   The user can correct any column in Column setup.
5. **Units.** Oxides, LOI, H2O+ and CO2 are used in **wt%**; elements in
   **ppm**.
   - The unit is read from the column name or a units row under the header.
   - Conversions: ppb ÷ 1000 → ppm; element in wt% × 10 000 → ppm; oxide in
     ppm ÷ 10 000 → wt%.
   - A column without a unit is taken as wt% (oxides) or ppm (elements).
     [App convention]
   - Every conversion is reported.
6. **K, Ti and P in ppm** are calculated from K2O, TiO2 and P2O5 when the
   element column is missing. Factors: K = 0.8301 K2O; Ti = 0.5995 TiO2;
   P = 0.4364 P2O5 (element mass fraction of the oxide).

## 2. Basic recalculations

| Quantity | Formula | Origin |
|---|---|---|
| FeOt (total iron as FeO) | FeOt if given; else FeO + 0.8998 × Fe2O3; else 0.8998 × Fe2O3t | stoichiometry: 2 FeO / Fe2O3 = 143.69 / 159.69 |
| Fe2O3t (for F-M-W) | 1.111 × FeOt | [Janoušek et al. 2006] |
| Anhydrous (volatile-free) oxides | oxide / (sum of SiO2, TiO2, Al2O3, iron, MnO, MgO, CaO, Na2O, K2O, P2O5) × 100 | Le Bas et al. 1986 [Source] |
| Mg# | 100 × Mg / (Mg + Fe²⁺), molar, with all iron as Fe²⁺ | common definition |
| Molar proportion | oxide wt% / molar mass | |
| Millications | 1000 × cations per formula × oxide wt% / molar mass | [Janoušek et al. 2006] |
| A/CNK, A/NK | Al2O3 / (CaO + Na2O + K2O); Al2O3 / (Na2O + K2O), molar | Shand (1943); plot after Maniar and Piccoli (1989) |

Notes:

- The anhydrous sum leaves out LOI, H2O+, CO2, Cr2O3 and NiO. In
  peridotites, Cr2O3 + NiO is often 0.4–0.7 wt%. This makes anhydrous
  values about 0.5 % (relative) higher than when these oxides are included.
  [App convention]
- When the file has FeO and Fe2O3, FeOt and Fe2O3t are not added again, so
  iron is never counted twice.
- Oxide ratios (for example MgO/SiO2) do not change with the anhydrous
  recalculation.

## 3. Iron oxidation state and the CIPW norm

- **CIPW norm.** Hutchison (1974, 1975), ported line by line from the
  implementation of Janoušek et al. (2006). [Janoušek et al. 2006] H2O+ and
  CO2 are used when the file has them (CO2 goes to calcite).
- **Iron split.** The norm and the Verma et al. (2006) diagrams need FeO and
  Fe2O3 separately.
  - Measured FeO and Fe2O3 are always used as they are.
  - If only total iron is known, it is split with the Fe³⁺/Fe(total) ratio
    *r* from Settings: FeO = FeOt × (1 − r) and Fe2O3 = FeOt × r / 0.8998.
    The default r = 0.15 is an [App convention].
- **What the sources say.**
  - Le Bas et al. (1986): use the FeO/Fe2O3 ratio stated by the analyst; if
    none is stated, calculate a standard ratio with the method of
    Le Maitre (1976).
  - Le Maitre et al. (2002, p. 34): if only total iron was measured, "it is
    up to the user to justify the method used for partitioning the iron".
  - The Le Maitre (1976) method is **not implemented yet**: its formula has
    not been checked against the original paper.
- **Serpentinised rocks.** Serpentinization oxidises Fe²⁺ in olivine and
  pyroxene to Fe³⁺ in serpentine and magnetite. The bulk-rock
  100·Fe2O3/(Fe2O3 + FeO) therefore rises with the degree of
  serpentinization (Deschamps et al. 2013; Paulick et al. 2006).
  - A fixed ratio is therefore not valid for these rocks.
  - The app warns when an ultramafic sample has no measured FeO (Data check,
    CIPW norm, Verma et al. 2006).

## 4. Screening before naming and plotting

All screening code is in `geochem/screening.py`.

### 4.1 Ultramafic samples

A sample is treated as ultramafic when **either** condition is true:

- its anhydrous MgO is at or above the threshold in Settings (default
  30 wt%) [App convention]; or
- its **Rock type** or **Group** text contains one of: serpentin-, peridot-,
  dunit-, harzburg-, lherzol-, wehrl-, pyroxenit-, websterit-, troctolit-,
  ultramafic. [App convention]

The flag only produces warnings and the MgO-deficit column. It never
removes data.

### 4.2 Order of IUGS names (TAS)

Le Maitre et al. (2002, p. 34 and Fig. 2.13, after Le Bas 2000) state that
some rocks must be identified **before** the TAS diagram is used. The app
applies these steps in order. All values are wt%, anhydrous. [Source]

1. **High-Mg volcanic rocks**:

   | Rule | Name |
   |---|---|
   | SiO2 > 52, MgO > 8, TiO2 < 0.5 | boninite |
   | 30 < SiO2 < 52, MgO > 18, Na2O + K2O < 2, TiO2 < 1 | komatiite |
   | 30 < SiO2 < 52, MgO > 18, Na2O + K2O < 2, TiO2 > 1 | meimechite |
   | 30 < SiO2 < 52, MgO > 12, Na2O + K2O < 3 | picrite |

   The komatiite and meimechite rules take precedence over the picrite rule.
   When TiO2 is missing, the name says that TiO2 is needed.
   [App convention]
2. **Nephelinites** (Le Bas 1989, as cited in Le Maitre et al. 2002, p. 36).
   Only samples in the TAS foidite or basanite/tephrite fields are tested,
   using the CIPW norm: ne > 20 % → nephelinite; ne < 20 % with ab present
   but < 5 % → melanephelinite. [Source]
3. Otherwise the name is the **TAS field** (Le Bas et al. 1986), found as
   described in chapter 6.

Two app conventions are added:

- A sample whose Rock type or Group names an ultramafic rock is reported as
  *TAS not applicable (ultramafic rock)*. Reason: TAS is for volcanic rocks
  (Le Bas et al. 1986), and the IUGS high-Mg rules are for volcanic rocks
  too. [App convention, based on the Source]
- The high-Mg rules use chemistry only, so a serpentinite or peridotite also
  passes the komatiite rule. If such a sample has MgO above the ultramafic
  threshold and no rock type, the name gets the reminder *(if volcanic; give
  Rock type for peridotites)*. [App convention]

The Results tab always shows both the **IUGS name** and the **TAS field**,
so you can see where the name came from.

### 4.3 Freshness for TAS

| Check | Rule | Origin |
|---|---|---|
| H2O+ | > 2 wt% → suspect | Le Bas et al. 1986, rule (e); Le Bas et al. 1992, rule 4 [Source] |
| CO2 | > 0.5 wt% → suspect | same [Source] |
| LOI (only if H2O+ and CO2 are missing) | > 2.5 wt% → suspect (proxy) | [App convention]: 2 + 0.5; LOI is not the same as H2O+ + CO2 |
| High-Mg rocks | limit withdrawn | Le Maitre et al. 2002, p. 33 [Source] |
| Ultramafic rock type | "not applicable" | [App convention] |

The flag is a warning only. Suspect samples are still plotted and named.

### 4.4 Relative MgO deficit (ultramafic samples)

MgO deficit (%) = 100 × [1 − (MgO/SiO2) / (1.107 − 2.598 × Al2O3/SiO2)]

- The denominator is the terrestrial array in oxide weight ratios, from
  Niu (2004, Fig. 2a). [Source]
- The formula assumes, as Niu (2004) did, that SiO2 and Al2O3 were immobile.
  Positive values mean MgO lost (or SiO2 gained).
- Niu (2004) found about 10 % relative MgO loss on average in abyssal
  peridotites, mostly from seafloor weathering. Snow and Dick (1995)
  estimated about 5 wt% MgO lost from the average dredged abyssal
  peridotite.
- The column itself (this formula applied to every sample) is an
  [App convention] built on Niu's equation.

## 5. Diagram calculations

The axis formulas of every diagram are shown in its **Scientific basis**
tab. The formulas come from the original papers and the templates of
Janoušek et al. (2006).
Special cases:

- **Discriminant-function diagrams** (Agrawal et al. 2008; Verma et al.
  2006). The function coefficients are copied from the templates of Janoušek et
  al. (2006) and stored in `geochem/diagrams/gcdkit/discriminants.json`.
  [Janoušek et al. 2006] Only
  samples with SiO2 < 52 wt% are plotted, as the papers require.
- **F-M-W (Ohta and Arai 2007).** [Source; checked against Janoušek et al. 2006]
  1. CaO is corrected for carbonate (CO2) and apatite (10/3 × mol P2O5).
  2. Missing or zero TiO2, CaO, Na2O and K2O are replaced by 0.005 wt%,
     because log(0) is undefined (paper, section 2). The implementation of
     Janoušek et al. (2006) sets them to 0
     instead, which loses the sample.
  3. The eight oxides are closed to 100 %.
  4. M, F and W are calculated with the coefficients of the paper's Table 4.
- **Ternary plots.** Each apex is factor × (sum of its columns). The three
  values are closed to 100 %. Plot coordinates: x = c + b/2, y = b·√3/2,
  with apex a left, b top, c right (as in Janoušek et al. 2006). Samples with a missing
  or negative value, or a zero total, are left out and listed.
- **Spider diagrams.** Sample (ppm) / normalising value (ppm). Values below
  detection limit are left out; dotted lines bridge the gaps. All 35
  normalising sets are those compiled by Janoušek et al. (2006), each with its
  reference.

## 6. Naming samples from a diagram (classification)

1. Each field of a diagram is a polygon taken from the template of
   Janoušek et al. (2006).
2. A sample gets the name of the polygon that contains its point. A point
   on a boundary (within 10⁻⁹) counts as inside. If fields overlap, the
   first field in the template wins. [App convention, as in the polygon test
   of Janoušek et al. 2006]
3. For diagrams with logarithmic fields, the test is done on log10 values.
4. Results:
   - outside every field → *Unclassified*;
   - a needed value missing → *No data*.
5. One typo in a template field name is corrected ("granodirite" →
   "granodiorite").

## 7. Visualisation

- **Boundaries.** Lines, field polygons, labels and axis limits are
  converted **unchanged** from the templates of Janoušek et al. (2006) by
  `tools/gcdkit_import.py`. A sample therefore falls in the same field as in
  their implementation. The template file of every diagram is named on the References
  page.
- **Elements added by GeoChem App** (not in Janoušek et al. 2006):
  - Paulick diagram: oceanic array MgO/SiO2 = 1.019 − 2.596 Al2O3/SiO2
    (dashed) and the abyssal peridotite box 0.01–0.07 Al2O3/SiO2,
    0.75–1.05 MgO/SiO2 (dotted), both from Niu (2004). [Source]
- **Check of the Paulick array.**
  - The template of Janoušek et al. (2006) draws the terrestrial array from
    (0, 1.10) to (0.10, 0.842).
  - Niu's equation gives 1.107 and 0.847 at the same points, which agrees
    within about 0.6 %.
  - Hart and Zindler (1986) give the array in metal weight ratios (Mg/Si,
    Al/Si), not oxide ratios. Their values are not mixed into this oxide
    plot.
- **Styles.** Screen styles and the *Publication* style change only colours
  and fonts, never positions. Figures are made with Matplotlib (SVG on
  screen; PNG, SVG or PDF on download).

## 8. Diagram-specific warnings

Some diagrams carry an extra warning, shown above their Results tab when
the data contain ultramafic samples:

| Diagram | Warning | Basis |
|---|---|---|
| F-M-W (Ohta and Arai 2007) | W rises with Ca and alkali loss, not only weathering. For example, an idealised harzburgite gives W ≈ 14; with CaO lowered to 0.05 wt% (serpentinization-type Ca loss) it gives W ≈ 76. | Ohta and Arai 2007 (scope, section 4); Deschamps et al. 2013 (Ca loss). The example is a calculation by GeoChem App with idealised compositions. |
| Verma et al. (2006) | The iron split is not reliable without measured FeO. | Deschamps et al. 2013; Paulick et al. 2006 |
| Nb/Y – Zr/Ti (Pearce 1996) | Success rates of the original Winchester and Floyd (1977) diagram: 17–76 % depending on rock type. | Verma et al. 2010 |
| Co – Th (Hastie et al. 2007) | Minimum misclassification 25–93 % in 7 of 14 tests; mainly useful for the series name of arc rocks. | Verma et al. 2010 |

## 9. All app conventions in one place

Report these in your methods section if they affect your results.

| Convention | Value | Where to change it |
|---|---|---|
| Fe³⁺/Fe(total) when only total iron is measured | 0.15 | Settings |
| Recalculate to 100 % volatile-free before TAS | on | Settings |
| Ultramafic threshold (anhydrous MgO) | 30 wt% | Settings |
| Ultramafic rock-type words | listed in 4.1 | `geochem/screening.py` |
| LOI proxy for freshness | 2.5 wt% | `geochem/screening.py` |
| Cells such as `<0.01` | missing, not zero or half the detection limit | — |
| Column without a unit | wt% (oxides), ppm (elements) | Column setup |
| Oxides left out of the anhydrous sum | LOI, H2O+, CO2, Cr2O3, NiO | — |
| Boundary points in classification | counted as inside | — |

## 10. Checks and tests

- **Diagrams and basic values.** `test_data/geochem_test_30.xlsx` stores
  the expected TAS field, AFM series and Mg# of 30 samples. The app
  reproduces all 30 TAS fields and all 30 AFM series. Mg# agrees within
  0.05, which is the rounding of the stored values.
- **XRF module.** Reproduces the published values of Mikuni et al. (2025)
  (user manual, chapter 14).
- **Version 0.13.0 screening.** Tested with synthetic samples of known
  type: serpentinite, komatiite, picrite, boninite, basalt and nephelinite.
  Each received the expected name.
- **F-M-W zero replacement.** Reproduces the idealised example in chapter 8.

## 11. References

Sources of the methods in this document. The original reference of every
diagram is on the **References** page and in each diagram's Scientific
basis tab.

- Deschamps F., Godard M., Guillot S., Hattori K. (2013) Geochemistry of
  subduction zone serpentinites: a review. Lithos 178, 96–127.
  doi:10.1016/j.lithos.2013.05.019
- Hart S.R., Zindler A. (1986) In search of a bulk-Earth composition.
  Chemical Geology 57, 247–267.
- Hutchison C.S. (1974) Laboratory Handbook of Petrographic Techniques.
  John Wiley and Sons, New York.
- Hutchison C.S. (1975) The norm, its variations, their calculation and
  relationships. Schweizerische Mineralogische und Petrographische
  Mitteilungen 55, 243–256.
- Janoušek V., Farrow C.M., Erban V. (2006) Interpretation of whole-rock
  geochemical data in igneous geochemistry: introducing Geochemical Data
  Toolkit (GCDkit). Journal of Petrology 47, 1255–1259.
  https://doi.org/10.1093/petrology/egl013
- Le Bas M.J. (1989) Nephelinitic and basanitic rocks. Journal of
  Petrology 30, 1299–1312. (as cited in Le Maitre et al. 2002)
- Le Bas M.J. (2000) IUGS reclassification of the high-Mg and picritic
  volcanic rocks. Journal of Petrology 41, 1467–1470. (as cited in
  Le Maitre et al. 2002)
- Le Bas M.J., Le Maitre R.W., Streckeisen A., Zanettin B. (1986) A chemical
  classification of volcanic rocks based on the total alkali-silica diagram.
  Journal of Petrology 27, 745–750. doi:10.1093/petrology/27.3.745
- Le Bas M.J., Le Maitre R.W., Woolley A.R. (1992) The construction of the
  Total Alkali-Silica chemical classification of volcanic rocks. Mineralogy
  and Petrology 46, 1–22. doi:10.1007/BF01160698
- Le Maitre R.W. (1976) Some problems of the projection of chemical data
  into mineralogical classifications. Contributions to Mineralogy and
  Petrology 56, 181–189. (as cited in Le Bas et al. 1986; not yet used)
- Le Maitre R.W. (ed.) (2002) Igneous Rocks: A Classification and Glossary
  of Terms. Recommendations of the International Union of Geological
  Sciences Subcommission on the Systematics of Igneous Rocks, 2nd edition.
  Cambridge University Press, Cambridge. ISBN 978-0-521-66215-4
- Maniar P.D., Piccoli P.M. (1989) Tectonic discrimination of granitoids.
  Geological Society of America Bulletin 101, 635–643.
- Mikuni K., Ishikawa A., Sato R. (2025) Geochemical Journal 59(6),
  299–314. (XRF module; full reference in the user manual, chapter 14)
- Niu Y. (2004) Bulk-rock major and trace element compositions of abyssal
  peridotites: implications for mantle melting, melt extraction and
  post-melting processes beneath mid-ocean ridges. Journal of Petrology 45,
  2423–2458.
- Ohta T., Arai H. (2007) Statistical empirical index of chemical weathering
  in igneous rocks: a new tool for evaluating the degree of weathering.
  Chemical Geology 240, 280–297.
- Paulick H., Bach W., Godard M., De Hoog J.C.M., Suhr G., Harvey J. (2006)
  Geochemistry of abyssal peridotites (Mid-Atlantic Ridge, 15°20'N, ODP
  Leg 209): implications for fluid/rock interaction in slow spreading
  environments. Chemical Geology 234, 179–210.
- Shand S.J. (1943) Eruptive Rocks. Their Genesis, Composition,
  Classification, and Their Relation to Ore-Deposits. John Wiley and Sons,
  New York.
- Snow J.E., Dick H.J.B. (1995) Pervasive magnesium loss by marine
  weathering of peridotite. Geochimica et Cosmochimica Acta 59, 4219–4235.
- Verma S.P., Rodríguez-Ríos R., González-Ramírez R. (2010) Statistical
  evaluation of classification diagrams for altered igneous rocks. Turkish
  Journal of Earth Sciences 19, 239–265. doi:10.3906/yer-0902-9
- Winchester J.A., Floyd P.A. (1977) Geochemical discrimination of
  different magma series and their differentiation products using immobile
  elements. Chemical Geology 20, 325–343. (as evaluated by Verma et al. 2010)
