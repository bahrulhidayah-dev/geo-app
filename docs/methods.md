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
| FeOt (total iron as FeO) | per sample: FeOt if given; else FeO + 0.8998 × Fe2O3; else 0.8998 × Fe2O3t | stoichiometry: 2 FeO / Fe2O3 = 143.69 / 159.69 |
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
- Iron is counted **once per sample** in the anhydrous sum: FeO + Fe2O3
  where either was measured, otherwise Fe2O3t, otherwise FeOt. This also
  holds when a file mixes the two forms (some rows with FeO and Fe2O3,
  others with total iron only). Before version 0.17.0 the total iron of
  such rows was left out of the sum, which raised their anhydrous SiO2.
  Files with one iron form give the same results as before.
- Oxide ratios (for example MgO/SiO2) do not change with the anhydrous
  recalculation.

## 3. Iron oxidation state and the CIPW norm

- **CIPW norm.** Hutchison (1974, 1975), ported line by line from the
  implementation of Janoušek et al. (2006). [Janoušek et al. 2006] H2O+ and
  CO2 are used when the file has them (CO2 goes to calcite).
- **Iron split.** The norm and the Verma et al. (2006) diagrams need FeO and
  Fe2O3 separately. Code: `geochem/iron.py`.
  - Measured FeO and Fe2O3 are used as they are (Le Bas et al. 1986:
    "taken as that stated by the analyst"), unless **Also replace measured
    FeO and Fe2O3** is switched on in Settings.
  - If only total iron T (as FeO) is known, every method gives the weight
    ratio R = Fe2O3/FeO. Then FeO = T / (1 + 0.8998 R) and Fe2O3 = R × FeO,
    so FeO + 0.8998 Fe2O3 = T exactly.
- **Methods (Settings).**
  - *Fixed ratio*: Fe³⁺/Fe(total) = *r* (atomic) for every sample:
    FeO = T × (1 − r), Fe2O3 = T × r / 0.8998. Default r = 0.15.
    [App convention] This was the default before version 0.17.1.
  - *Le Maitre (1976), volcanic* (**default** since 0.17.1): Ox = 0.93 − 0.0042 SiO2 − 0.022 (Na2O +
    K2O), regression on 12,962 volcanic rocks. *Plutonic*: Ox = 0.88 −
    0.0016 SiO2 − 0.027 (Na2O + K2O), 9,604 plutonic rocks. Ox =
    FeO/(FeO + Fe2O3) by weight, so R = (1 − Ox)/Ox. [Source] Le Bas et
    al. (1986) recommend this method when only total iron is given. Their
    classification is for volcanic rocks, so the volcanic equation is the
    default; choose the plutonic equation for plutonic rocks.
    [App convention]
    - SiO2 and Na2O + K2O are taken on an anhydrous basis, as for TAS; the
      paper does not state the basis. [App convention]
    - Ox is kept between 0.05 and 1. [App convention]
  - *Middlemost (1989)*: standard Fe2O3/FeO for each TAS field of Le Bas
    et al. (1986) (Table I): picrobasalt 0.15; basalt 0.20; basaltic
    andesite 0.30; andesite 0.35; dacite 0.40; rhyolite 0.50; trachybasalt
    0.30; basaltic trachyandesite 0.35; trachyandesite 0.40;
    trachyte/trachydacite 0.50; phonotephrite 0.35; tephriphonolite 0.40;
    phonolite 0.50; tephrite/basanite 0.20 if Na2O + K2O < 6 %, else 0.30
    (section 4); foidite 0.4 if Na2O + K2O > 10 %, 0.3 for 7–10 %, 0.2 for
    3–7 %, 0.1 below 3 %. [Source]
    - The TAS field is found on an anhydrous basis with total iron.
      Na2O + K2O exactly 6 % counts as ≥ 6 %. [App convention]
    - Samples outside every TAS field get the fixed ratio of Settings, and
      the app counts them. [App convention]
    - Middlemost (1989) derived these ratios for **volcanic** rocks. His
      values are lower than the Le Maitre (1976) means because he aimed at
      fresh rocks: the Le Maitre data include many oxidised rocks.
- **What the sources say.**
  - Le Bas et al. (1986): use the FeO/Fe2O3 ratio stated by the analyst; if
    none is stated, calculate a standard ratio with the method of
    Le Maitre (1976).
  - Le Maitre et al. (2002, p. 34): if only total iron was measured, "it is
    up to the user to justify the method used for partitioning the iron".
  - Middlemost (1989): for classifications that use the norm, standardise
    the ratio of **all** analyses, because raw ratios of altered rocks give
    spurious norms (switch *Also replace measured FeO and Fe2O3*).
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
- **Saccani (2015) second-step diagrams.** [Source] Two diagrams for
  ophiolitic basalts that overlap on the NbN–ThN diagram. Neither has a
  template of Janoušek et al. (2006); the separation lines are drawn from
  the coordinates given in the paper.
  - (Ce/Yb)N–(Dy/Yb)N, G-MORB vs N-MORB (Fig. 8; section 5.2): line from
    (0.4, 1.5) to (2, 0.9), i.e. (Dy/Yb)N = 1.65 − 0.375 (Ce/Yb)N. Use for
    samples in the N-MORB field of NbN–ThN.
  - DyN–YbN, boninite vs IAT (Fig. 9; section 5.3): line from (7, 25) to
    (9.5, 0). Use for samples in the IAT field of NbN–ThN.
  - Chondrite values of Sun and McDonough (1989): Ce 0.612, Dy 0.254,
    Yb 0.170 ppm (as listed in Rollinson and Pease 2021, Table 4.7). The
    paper names the source but not the numbers.
  - The paper draws the G-MORB/N-MORB line only between its two end
    points. The app extends it to the frame (dotted) so that every sample
    inside the axis limits gets a field. Samples outside the axis limits of
    the paper (0–2.5 and 0.5–2; 0–25 and 0–25) are *Unclassified*.
    [App convention]
  - The lines were drawn by eye (Saccani 2015, section 7); the paper reports
    96–100 % correct classification of its training samples.
- **Deschamps et al. (2013) LOI diagrams.** [Source: Figs. 3a, 4d, 4f]
  - Anhydrous basis of the paper: SiO2 and Sum = MgO + Fe2O3(total) + Al2O3
    + TiO2 + CaO + Cr2O3 + MnO + NiO + Na2O + K2O + P2O5, closed to 100 %.
    This sum differs from the anhydrous sum of section 2 (it includes Cr2O3
    and NiO, and iron is taken as Fe2O3(total) = FeOt / 0.8998).
  - Cr2O3 = 1.4616 × Cr (ppm) / 10,000 and NiO = 1.2725 × Ni (ppm) / 10,000
    when the oxides are not in the file; a missing minor oxide counts as 0.
    SiO2, MgO and iron are required. [App convention]
  - Ternary: LOI × 10 (top), SiO2 (right), Sum (left). LOI is as measured.
    Lines: SiO2/Sum = 0.81 (mean of 899 serpentinites, paper Fig. 3a) and
    equal LOI of 2.5, 5, 10, 12, 16 and 20 wt%.
  - Mineral points are ideal Mg end-members calculated from their formulas:
    brucite (SiO2 0, LOI 30.9), serpentine Mg3Si2O5(OH)4 (anhydrous SiO2
    49.85, MgO 50.15, LOI 13.0), talc (66.53, 33.47, 4.75), forsterite
    (42.71, 57.29, 0) and enstatite (59.85, 40.15, 0) wt%. The paper's Fig.
    4d plots natural lizardite and antigorite compositions, which are not
    given in the text and are not copied. [App convention]
- **Fe redox in serpentinites (Paulick et al. 2006).** [Source: Figs. 6D,
  11A]
  - Only samples with FeO **and** Fe2O3 measured are plotted. Values from
    the iron split (section 3) are never used, because they would only
    reproduce the chosen ratio. A file without both columns gives "Missing
    data". [App convention]
  - FeO and Fe2O3 are recalculated to 100 % anhydrous (section 2), as in the
    paper's Fig. 6.
  - Magnetite line: Fe2O3/FeO = 159.69 / 71.84 = 2.2227 by weight
    (stoichiometry of Fe3O4 = FeO·Fe2O3); Fe³⁺/Fe(total) = 2/3.
  - Lines of equal total iron: FeO + 0.8998 Fe2O3 = 4, 6, 8 and 10 wt%. The
    paper draws one such line for its own samples. [App convention]
  - Fe³⁺/Fe(total) (atomic) = 0.8998 Fe2O3 / (FeO + 0.8998 Fe2O3).
  - The x axis is LOI. Paulick et al. plotted H2O, which they measured or
    calculated from LOI, CO2, S and NO3. [App convention]
- **Trace elements vs Yb in serpentinites (Deschamps et al. 2013).**
  [Source: Figs. 7a, 7d, 11] Log–log plots of Ti, La/Yb, Li, B, Cs, Sr, Ba,
  U, Pb, As and Sb (ppm) against Yb (ppm), as measured (no recalculation).
  Reference points: primitive mantle (McDonough and Sun 1995, Table 5:
  Yb 0.441, Ti 1205, La 0.648, Li 1.6, B 0.30, Cs 0.021, Sr 19.9, Ba 6.6,
  U 0.0203, Pb 0.150, As 0.05, Sb 0.0055 ppm) and depleted mantle (Salters
  and Stracke 2004, Table 6: Yb 0.401, Ti 798, La 0.234, Li 0.70, B 0.060,
  Cs 0.00132, Sr 9.80, Ba 1.20, U 0.0047, Pb 0.0232, As 0.0074, Sb 0.0026
  ppm). The paper's fields were drawn by hand around its data and are not
  copied. [App convention]
- **V–MgO melting curves (Lee et al. 2003).** [Source: eqs. 1–3, Table 1,
  Fig. 4A] Calculated by `tools/lee2003_vmgo.py` and stored as diagram
  geometry.
  - Fractional melting at 1.5 GPa by small equilibrium increments (eq. 1):
    Cs(j+1) = D Cs(j) / (D (1 − ΔF) + ΔF), with ΔF the fraction of the
    remaining residue melted in each 0.1 % step of F. Starting V = 87 ppm.
  - Residue MgO and modes (opx, cpx, olivine, spinel) interpolated
    linearly in F between the rows of Table 1 (1.5 GPa, pMELTS), up to
    F = 46.6 % (MgO 48.0 wt%). [App convention: linear interpolation]
  - Partition coefficients (eq. 2, Canil 2002): D = a / (10^(b ΔNNO + c) +
    1) for cpx (8, 0.31, 1.22), olivine (0.9, 0.31, 1.53) and spinel (18.5,
    0.37, 0.62); D(opx) = 0.116 exp(−0.215 ΔNNO).
  - ΔNNO from ΔFMQ with the buffer equations of Frost (1991) (eq. 3) at
    P = 15,000 bar and T = 1350 °C: ΔNNO = ΔFMQ − 0.136. The paper does not
    give the temperature used; between 1250 and 1450 °C the offset changes
    by less than 0.03 log units. [App convention]
  - Samples: V (ppm) as measured against anhydrous MgO (section 2).
- **Ternary plots.** Each apex is factor × (sum of its columns). The three
  values are closed to 100 %. Plot coordinates: x = c + b/2, y = b·√3/2,
  with apex a left, b top, c right (as in Janoušek et al. 2006). Samples with a missing
  or negative value, or a zero total, are left out and listed.
- **Spider diagrams.** Sample (ppm) / normalising value (ppm). Values below
  detection limit are left out; dotted lines bridge the gaps. All 35
  normalising sets are those compiled by Janoušek et al. (2006), each with its
  reference.
- **Variation diagrams** (Plots → Variation diagrams; `geochem/variation.py`).
  - *Harker diagrams*: SiO2 on the x axis against every major oxide. This
    type of variation diagram was popularised by Harker (1909, as cited in
    Rollinson and Pease 2021, section 3.3). SiO2 is chosen because it is
    the main constituent and usually varies most (Rollinson and Pease 2021,
    section 3.3.2).
  - *MgO variation diagrams*: MgO on the x axis. Rollinson and Pease (2021,
    section 3.3.2) recommend MgO for mafic and ultramafic suites, whose SiO2
    range is small, because MgO is held in olivine and pyroxene and varies
    strongly with melting or crystal removal. The same plots are used for
    peridotites and serpentinites (Niu 2004; Deschamps et al. 2013).
  - *Reading the trends.* Most trends are mixing lines: between magmas,
    between a melt and crystals that are added or removed (fractional
    crystallisation, accumulation), during partial melting, or between
    sediment components. Partial melting and fractional crystallisation can
    give the same trend on major-element plots; trace elements, isotopes
    and mineral compositions plotted on the same diagram help to tell them
    apart (Rollinson and Pease 2021, section 3.3.1).
  - *Closure.* Because oxides sum to 100 %, some correlations, especially
    against SiO2, can be produced by the constant sum alone. Aitchison and
    Egozcue (2005, as cited in Rollinson and Pease 2021) called Harker
    diagrams misleading. Rollinson and Pease (2021, section 3.3.2.2) answer
    that bivariate plots give geologically meaningful results in practice.
    They advise testing trends against a specific hypothesis. GeoChem App
    shows the plots and leaves this judgement to the user.
  - Panels: TiO2, Al2O3, FeOt, MnO, MgO or SiO2, CaO, Na2O, K2O and P2O5,
    when present; FeOt = FeO + 0.8998 Fe2O3.
  - Basis: *anhydrous* (default; the same recalculation as for TAS,
    chapter 2) or *as measured*. [Source: Le Bas et al. 1986; Niu 2004;
    Deschamps et al. 2013]
  - Trace elements chosen by the user are plotted as measured, without the
    anhydrous recalculation. [App convention] Default: none for Harker
    diagrams; Ni and Cr for MgO diagrams, when present. [App convention]
  - All panels share one x range, so they can be compared. [App convention]
  - Mg# is 100 × Mg/(Mg + Fe²⁺) in atomic proportions with all iron as
    Fe²⁺, the definition used by Rollinson and Pease (2021, section 3.3.2,
    e). They note that several definitions exist and that the one used
    should always be stated.
  - *Iso-Mg# lines* on the FeOt panel (MgO diagrams only):
    FeOt = MgO × (71.844 / 40.304) × (100 / Mg# − 1), all iron as Fe²⁺, for
    Mg# 85, 87.5, 90, 92.5 and 95 (Deschamps et al. 2013, Fig. 3b).
  - *Olivine line*: the straight line from forsterite (MgO 57.30 wt%) to
    fayalite (FeO 70.51 wt%). Mixing by mass is linear, so all olivine
    compositions lie on it (Deschamps et al. 2013, Fig. 3b).
  - Both lines can be *Auto* (shown only when the data contain ultramafic
    samples, chapter 4.1), *Always* or *Off*. Default: Auto.
    [App convention]

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
    plot. (Rollinson and Pease 2021, section 3.3.2 d, give the same
    conversion: element wt% = 0.529 Al2O3, 0.467 SiO2, 0.603 MgO.)
- **Text positions changed by GeoChem App.** In the TAS diagram the label
  "Trachyte / Trachydacite" is moved from (63.5, 11.2) to (66.0, 11.6), the
  middle of its field, so it no longer crosses the 63 wt% SiO2 line. The
  labels "Alkaline" and "Subalkaline/Tholeiitic" name series, not fields;
  they are never replaced by numbers. Only labels move; no boundary
  changes. [App convention]
- **Field names as numbers** (Plot appearance → Field names → Numbers).
  Field names longer than five characters are replaced by a number, and a
  key below the plot lists the names. Short abbreviations (VAG, ORG, IAT …)
  stay as text. [App convention]
- **Sample labels** (Plot appearance → Sample labels). Labels only
  change the display; they never change a value or a classification.
  [App convention]
  - *Auto-arrange* (default): for each label, eight positions around its
    point are tried, first next to the point and then at two larger
    distances. The position with the least overlap with other labels,
    data points, other text (field names), the legend and the plot edge is
    kept. A label placed away from its point gets a thin leader line. The
    search has no random step, so the same data always give the same plot.
    Labels of points outside the plot are not drawn.
  - *Fixed*: every label at the upper right of its point.
  - *Numbers*: each sample gets a number (in data order, the same number in
    every panel), and a key below the plot lists the sample names.
  - All labels have a thin outline in the background colour so that they
    stay readable over lines.
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

## 8a. Mass change (isocon analysis)

Page *Tools → Mass change*; code in `geochem/masschange.py`.

- **Isocon** (Grant 1986, 2005). [Source] Cᴬ = (M°/Mᴬ) C° for immobile
  species. The slope s = M°/Mᴬ is the mean of Cᴬᵢ/C°ᵢ over the immobile
  species chosen by the user (Grant 2005, Table 1). This mean does not
  depend on units or display scaling. A least-squares slope through the
  origin is also available in the code for comparison; it depends on the
  units (Grant 2005).
- **Gains and losses.** ΔCᵢ/C°ᵢ = (Mᴬ/M°)(Cᴬᵢ/C°ᵢ) − 1 = (Cᴬᵢ/C°ᵢ)/s − 1,
  and ΔCᵢ = C°ᵢ × ΔCᵢ/C°ᵢ, in the unit of each species, per 100 g of
  original rock. Overall mass change ΔM/M° = 1/s − 1.
- **Same as MacLean and Barrett (1993).** Their enrichment factor EF =
  C°imm/Cᴬimm = 1/s; reconstructed composition RC = EF × Cᴬ; mass change of
  each component dX = RC − C°.
- **Immobility test** (MacLean and Barrett 1993). [Source] Within one
  precursor unit, each species against a reference species: Pearson r,
  least-squares slope through the origin, and the intercept of an ordinary
  regression as % of the mean. r ≥ 0.90 is marked "behaves immobile"; the
  paper reports r ≈ 0.90–0.99 for immobile pairs.
- **Display.** Species are scaled for the isocon diagram as in Grant (2005,
  Table 1, panel C): oxides first, then trace elements, each sorted by C°
  and given evenly spaced plotting values. Species with Cᴬ above 1.6 times
  the largest scaled C° are drawn at the top edge with their Cᴬ/C°.
  [App convention]
- **Warning.** When the immobile species chosen differ in Cᴬ/C° by more
  than 10 % (coefficient of variation), the page warns that some of them
  were probably mobile. [App convention]
- C° may be a single sample or the mean of a group, as Grant (2005)
  recommends averaging several least-altered samples.

## 8b. Mineral modes (least squares with closure)

Page *Tools → Mineral modes*; code in `geochem/modes.py`.

- **Mass balance** (Albarède 1995, section 5.3.1). [Source] The rock
  composition y (m components) is a mixture of n minerals with known
  compositions (the columns of A): y = A x, where x holds the mass
  fractions of the minerals. With more components than minerals the
  system is solved by least squares.
- **Closure condition.** The fractions must add up to 1. Albarède (1995)
  adds this with a Lagrange multiplier λ. With J = (1, …, 1)ᵀ:
  - unconstrained solution x₀ = (AᵀA)⁻¹Aᵀy;
  - λ = (1 − Jᵀx₀) / (Jᵀ(AᵀA)⁻¹J);
  - constrained solution x = x₀ + λ(AᵀA)⁻¹J.

  All values are divided by 100 first (wt% → fractions), as in the book.
  When AᵀA is singular the same problem is solved as one bordered system
  [AᵀA J; Jᵀ 0][x; μ] = [Aᵀy; 1] (minimum-norm solution).
- **Components.** SiO2, Al2O3, FeOt, MgO, CaO and H2O. All iron is FeOt;
  magnetite is therefore entered as 93.1 % FeOt (3 FeO per Fe3O4). H2O is
  H2O+ when present, otherwise LOI. [App convention: LOI also contains CO2
  and S; in serpentinites it is mostly H2O.] The analysis is used as
  measured (not anhydrous), because H2O is a component.
- **Normalisation.** The closure condition assumes that the rock and every
  mineral add up to the same total over the components used. Real
  analyses do not (minor oxides are left out; Fe2O3 is recast as FeO), nor
  does magnetite written as FeOt. The app therefore scales the rock and
  each mineral to 100 % over the components used, solves, and converts
  back to mass fractions: xᵢ = (x′ᵢ/sᵢ) / Σⱼ(x′ⱼ/sⱼ), where sᵢ is the
  original sum of mineral i. [App convention] Without this step a rock
  analysis that is 3 % short gives modes wrong by up to 4 % (absolute) in
  the test below; with it the modes are exact.
- **Mineral compositions.** Ideal end-members by default (olivine Fo90,
  orthopyroxene En90, diopside, MgAl2O4 spinel, Mg-serpentine, brucite,
  magnetite, talc, clinochlore). [App convention] They can be replaced on
  the page by measured (for example EPMA) compositions, and new minerals
  can be added.
- **Which minerals can be resolved.** At most as many minerals as
  independent components. The app checks the rank of the equations
  (component rows plus the closure row) and their condition number
  (ratio of the largest to the smallest singular value). Rank < n: the
  modes are not unique. Condition number > 300: the modes are unstable.
  [App convention] Brucite is not in the default set: serpentine = 2
  enstatite + brucite + H2O, so with olivine, orthopyroxene and serpentine
  the condition number is about 5000 and an analytical error of 1 %
  changes the modes by more than 100 %.
- **Uncertainty.** Monte Carlo: the analysis is varied 300 times with
  normal errors of 1 % relative, at least 0.05 wt% (1σ) [App convention],
  and the spread of the modes is reported as ±1σ.
- **Quality of the fit.** Residuals (measured − calculated, wt%) and their
  sum of squares. A negative mode means that the mineral is probably
  absent, or that its composition does not fit.
- Modes are mass fractions, not volume fractions.

## 8c. Hydrogen generation by serpentinization

Page *Tools → Hydrogen generation*; code in `geochem/hydrogen.py`. All
equations are from Rezaee (2025). They are empirical: a regression on 14
laboratory experiments (mostly powdered olivine and peridotite) with
R² ≈ 0.86. Natural rocks react more slowly (grain size, water supply,
fracture density), so the results are an order of magnitude, not a
measurement. Rezaee (2025) says this himself.

- **Reaction.** [Source] Fe²⁺ in olivine and pyroxene is oxidised to Fe³⁺
  (in magnetite and serpentine) and water is reduced to H₂:
  2FeO + H₂O → Fe₂O₃ + H₂.
- **Generation rate RH2** (mmol H₂ per kg of rock; T in °C, P in bar).
  [Source]
  - Eq. 3: RH2 = 3.102 + 0.12 T + 0.073 P, for T up to 315 °C.
  - Eq. 4: RH2 = 0.43 T − 9.33, for T below 315 °C (no pressure term).
  - Eq. 5: RH2 = −1.38 T + 571.3, for 315–400 °C.
  - Above 400 °C olivine is stable with water: RH2 = 0.
  The app uses Eq. 3 when a pressure is given and Eq. 4 when it is not.
  [App convention] Negative values (Eq. 4 below about 22 °C) are set to 0;
  below 0 °C no rate is given. The equations do not join at 315 °C
  (Eq. 4 gives 126, Eq. 5 gives 137 mmol/kg; Eq. 3 depends on P), so the
  curve has a step there. This is a property of the published equations.
- **Correction factor C.** [Source] C = Σ (mass fraction × rank), with
  rank 1.0 for olivine, 0.7 for orthopyroxene, 0.5 for clinopyroxene and
  0 for all minerals that do not take part (Table 2). Example of the
  paper: 60 % olivine + 40 % orthopyroxene → C = 0.88. C = 1 when the
  composition is unknown. The paper states that the ranks are the
  author's provisional judgment, not experimental values.
  [App convention] On the Per sample tab C comes from the mineral modes
  (default minerals of Tools → Mineral modes); negative modes are set to
  0. Spinel, serpentine, magnetite, brucite, talc and chlorite get rank 0.
- **Temperature from depth.** [Source] T = surface temperature + gradient
  × depth; the paper uses 23 °C and 30 °C/km.
- **Pressure from depth.** The paper means the pore pressure of water in
  open fractures but does not say how it was calculated. [App convention]
  Hydrostatic: P = 1000 kg/m³ × g × z (about 98 bar/km). Lithostatic:
  P = rock density × g × z (about 294 bar/km at 3000 kg/m³). g = 9.81 m/s².
  With a Depth column on the Per sample tab, hydrostatic pressure is used
  when the first tab uses a pressure.
- **Volumetric total GH2.** [Source] Eqs. 6–8:
  GRV = area × thickness; GRM = GRV × density;
  GH2 (kg) = 2 × 10⁻⁶ × GRM × C × RH2. The factor 2 × 10⁻⁶ converts mmol
  of H₂ to kg (H₂ taken as 2 g/mol, as in the paper). As in the paper's
  example, the body is divided into depth intervals (default 100 m) with
  the same area from top to base; each interval uses its own mass and the
  RH2 at its mid depth, and the intervals are added. An optional *fraction
  that reacted* multiplies the total (the paper uses 0.01 for the Giles
  Complex).
- **Other units.** [App convention] mol uses the true molar mass of H₂
  (2.016 g/mol); m³ at 0 °C and 1 atm uses 22.414 L/mol.

## 8d. Hydrogen already generated (degree of serpentinization)

Tab *Already generated (serpentinization degree)* of Tools → Hydrogen
generation; code in `geochem/hydrogen.py` (`degree_table`). It answers a
different question from section 8c: not "how fast could this rock make
H₂ at this temperature?" but "how much H₂ has this rock already made?".
It needs only total iron and LOI, so it works with ordinary XRF data.

- **Yield of complete serpentinization.** [Source] Liu et al. (2023):
  reactions of mantle olivine (Fo90) that put the Fe into magnetite or
  into Fe³⁺-serpentine use 15 mol of olivine per mol of H₂, which is at
  most 454 mmol H₂ per kg (checked: 15 × 0.1470 kg = 2.205 kg per mol).
  Any Fe²⁺ left in serpentine or brucite lowers this. With about half of
  the Fe in serpentine trivalent (Klein et al. 2009; Andreani et al. 2013,
  as cited in Liu et al. 2023) the yield is **227 mmol/kg**, the default.
  Thermodynamic models of serpentinized mantle give **150–300 mmol/kg**
  (Albers et al. 2021, as cited in Liu et al. 2023), the default low and
  high yields. All three can be changed on the page.
- **Degree of serpentinization S.** [App convention] Two ways, shown side
  by side:
  - from water: S = H₂O / 13.0 wt%, the water of pure serpentine
    Mg₃Si₂O₅(OH)₄ (2 × 18.015 / 277.11). Water is H2O+ when the file has
    it, otherwise LOI − CO2 when CO2 is given, otherwise LOI;
  - from the serpentine mode of section 8b (default minerals): S =
    serpentine wt% / 100.
  S is limited to 0–1. Both assume that serpentine is the only hydrous
  mineral: brucite (31 wt% H₂O), chlorite, amphibole or carbonate in the
  LOI make S too high.
- **H₂ already generated** = S × yield, with the low and high yields as a
  range. [App convention] The result is per kg of the analysed rock; the
  mass added by water (up to 13 %) is not corrected.
- **Which samples.** [App convention] Only ultramafic samples (section
  4.1). The yield is for olivine-rich mantle rock; serpentinization of
  pyroxenite makes Fe-rich serpentine and no magnetite, and less H₂ (Klein
  et al. 2013), so pyroxenites get a note.
- **Notes per sample:** pyroxenite; water above pure serpentine (brucite
  or other hydrous minerals?); S from water and from the mode differ by
  more than 0.15. The page also says how many samples use LOI as water.
- **Not used:** splitting total iron into FeO and Fe2O3 with a fixed ratio
  or an igneous regression (section 3) to calculate H₂ from Fe2O3. The H₂
  would only repeat the chosen ratio. Measured FeO and Fe2O3 are needed for
  an H₂ estimate from the oxidised iron (planned).
- **Not the H₂ in the rock today.** The result is the H₂ made during
  serpentinization. Most of it left the rock long ago, or was used to make
  methane.

## 9. All app conventions in one place

Report these in your methods section if they affect your results.

| Convention | Value | Where to change it |
|---|---|---|
| Iron split when only total iron is measured | Le Maitre (1976), volcanic equation, as recommended by Le Bas et al. (1986) (alternatives: plutonic equation, Middlemost 1989, fixed ratio 0.15) | Settings |
| Measured FeO and Fe2O3 | kept (can be standardised) | Settings |
| Le Maitre (1976) inputs | anhydrous SiO2 and Na2O + K2O; Ox kept in 0.05–1 | — |
| Middlemost (1989) outside TAS fields | fixed ratio of Settings | Settings |
| Recalculate to 100 % volatile-free before TAS | on | Settings |
| Ultramafic threshold (anhydrous MgO) | 30 wt% | Settings |
| Ultramafic rock-type words | listed in 4.1 | `geochem/screening.py` |
| LOI proxy for freshness | 2.5 wt% | `geochem/screening.py` |
| Cells such as `<0.01` | missing, not zero or half the detection limit | — |
| Column without a unit | wt% (oxides), ppm (elements) | Column setup |
| Oxides left out of the anhydrous sum | LOI, H2O+, CO2, Cr2O3, NiO | — |
| Boundary points in classification | counted as inside | — |
| Field counts chart (Results tab) | sorted by count; unclassified, no data and "not applicable" samples in grey at the bottom; percentages of all samples shown | — |
| Variation diagrams: basis | anhydrous | Variation diagrams page |
| Variation diagrams: trace elements | as measured; Ni and Cr by default on MgO diagrams | Variation diagrams page |
| Variation diagrams: iso-Mg# and olivine lines | Auto (only with ultramafic samples) | Variation diagrams page |
| Variation diagrams: panels per row | 3 | Variation diagrams page |
| Sample labels | Auto-arrange (least overlap, 8 positions × 3 distances) | Plot appearance |
| Field names | rotated along boundaries (Janoušek et al. 2006); numbers optional | Plot appearance |
| Mineral modes: H2O | H2O+, otherwise LOI | — |
| Mineral modes: rock and minerals scaled to 100 % over the components used | on | `geochem/modes.py` |
| Mineral modes: unstable when the condition number exceeds | 300 | `geochem/modes.py` |
| Mineral modes: analytical error for the ±1σ | 1 % relative, at least 0.05 wt% | `geochem/modes.py` |
| Mineral modes: default minerals | olivine Fo90, orthopyroxene En90, diopside, spinel, serpentine, magnetite (ideal) | Mineral modes page |
| Hydrogen: equation below 315 °C | Eq. 3 with a pressure, Eq. 4 without | Hydrogen generation page |
| Hydrogen: pressure from depth | hydrostatic (1000 kg/m³) or lithostatic (rock density), g = 9.81 m/s² | Hydrogen generation page |
| Hydrogen: negative rates (Eq. 4 below about 22 °C) | set to 0 | `geochem/hydrogen.py` |
| Hydrogen: minerals with rank 0 in C | all except olivine, orthopyroxene and clinopyroxene | `geochem/hydrogen.py` |
| Hydrogen: C on the Per sample tab | from the mineral modes (default minerals); negative modes set to 0 | `geochem/hydrogen.py` |
| Hydrogen: depth interval | 100 m, same area from top to base | Hydrogen generation page |
| Hydrogen already generated: yield | 227 mmol/kg, range 150–300 (Liu et al. 2023) | Hydrogen generation page |
| Hydrogen already generated: degree of serpentinization | H₂O / 13.0 wt% (water: H2O+, else LOI − CO2, else LOI), or serpentine mode / 100; limited to 0–1 | Hydrogen generation page |
| Hydrogen already generated: samples | ultramafic only; note for pyroxenites | `geochem/hydrogen.py` |
| Hydrogen already generated: S from water and from mode differ | note above 0.15 | `geochem/hydrogen.py` |
| TAS label "Trachyte / Trachydacite" | moved to (66.0, 11.6) | `TAS.json` |

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
- **Variation diagrams (0.14.0).** For a test basalt, anhydrous SiO2 and
  FeOt equal the hand calculation. A point on the Mg# 90 line has
  Mg# = 90.0. Fo90 olivine lies on the olivine line and has Mg# = 90.0.

- **V–MgO melting curves (0.23.0).**
  - The partition coefficients at ΔFMQ = 0 (olivine 0.028, cpx 0.50,
    spinel 3.9, opx 0.12) agree with Lee et al. (2003, Fig. 3).
  - The FMQ curve reproduces their Fig. 4A within about 2 ppm (for example
    14 ppm V at 44.6 wt% MgO; read from the figure: about 14.5).
  - The more reduced curves are higher than in the figure: FMQ−3 by up to
    about 10 ppm at MgO > 44 wt%. The paper's curves come from finer pMELTS
    steps than the 10 rows of Table 1; read fO2 estimates from the reduced
    curves as approximate (± 0.5 log unit).
  - 80 % of 335 harzburgites, lherzolites and dunites of the global
    database (Gard et al. 2019; MgO 37.5–48 wt%) plot between the FMQ−3 and
    FMQ curves, as Lee et al. (2003) report for oceanic mantle; 64 % of 292
    serpentinites do, and 30 % plot below FMQ (MgO loss or V loss).

- **Mass change (0.24.0).**
  - Grant (2005, Table 1; data of Mori et al. 2003): with SiO2, TiO2,
    Al2O3 and Cu as immobile species the app gives slope 0.9987 (paper
    0.999); the least-squares slope with Cu in ppm is 0.978 (paper 0.978).
    All ΔC values agree with the paper's column 6 within its rounding:
    0.011 wt% or less for oxides, 0.6 ppm or less for trace elements (for
    example K2O +2.63 wt%, CO2 +7.68 wt%, Ba +60 ppm).
  - Synthetic serpentinization with a known answer: a harzburgite to
    which 15 g H2O (as LOI) were added and 0.6 g CaO removed per 100 g.
    With SiO2, MgO and FeOt immobile (as Paulick et al. 2006) the app
    returns ΔLOI = +15.0, ΔCaO = −0.6 and mass change +14.4 %.
  - Immobility test on a synthetic suite (one precursor diluted by 0–30 %):
    TiO2, Zr and Yb against Al2O3 give r = 0.94–0.97; randomised CaO and
    Na2O give r ≈ 0.

- **Trace elements vs Yb (0.22.0).** Tested with 289 serpentinites of the
  global database with Yb (16–273 per element; values at or below zero,
  i.e. below detection, set to missing). La/Yb of the first sample: hand
  2.6207, app 2.6207. The reference values were read from the tables of
  McDonough and Sun (1995) and Salters and Stracke (2004); the PM values
  agree with the primitive-mantle set already in the app. As in the paper's
  Fig. 11, Cs, U, Pb, As, Sb and B of most serpentinites lie one to three
  orders of magnitude above the mantle values.

- **Fe redox diagram (0.21.0).** Tested with 134 serpentinites of the
  global database of Gard et al. (2019) that have FeO, Fe2O3 and LOI
  (duplicates removed). For the first sample (FeO 0.28, Fe2O3 8.10 wt%)
  the hand calculation gives Fe³⁺/Fe(total) = 0.963; the app gives the
  same, and the anhydrous FeO and Fe2O3 agree to 0.001 wt%. A file with
  total iron only gives "Missing data", so split iron is never plotted.
  Observations, not rules: the median Fe³⁺/Fe(total) is 0.71 (IQR
  0.52–0.77), and 77 of the 134 samples lie above the magnetite ratio, so
  Fe³⁺ is also held in other minerals (for example serpentine). Fe2O3 and
  LOI are not correlated in this mixed global set (r = −0.15), unlike the
  single drill hole of Paulick et al. (2006, Fig. 11A; R² = 0.68).

- **Deschamps et al. (2013) diagrams (0.20.0).** For UB-N (values of the
  example data: SiO2 39.43, MgO 35.21, Fe2O3t 8.34, LOI 10.44 wt%, Cr 2300
  and Ni 2000 ppm) a hand calculation gives anhydrous SiO2 44.78, MgO 39.98
  and SiO2/Sum 0.811; the app gives the same values. UB-N plots on the 0.81
  line, as in the paper's Fig. 3a. Mineral points and lines match Fig. 3a.

- **Saccani (2015) diagrams (0.19.0).** The N-MORB composition of Sun and
  McDonough (1989) (Ce 7.5, Dy 4.55, Yb 3.05 ppm) gives (Ce/Yb)N = 0.683 and
  (Dy/Yb)N = 0.998 by hand; the app gives the same values and the field
  N-MORB (the line lies at 1.394 for this (Ce/Yb)N). A synthetic boninite
  (Dy 0.9, Yb 0.6 ppm) falls in the boninite field and an IAT (Dy 3.4, Yb 2.3
  ppm) in the IAT field. The plotted lines match Figs. 8 and 9 of the paper.

- **Example datasets (0.16.0).** Each set was loaded and every page and
  all 27 diagrams were drawn without error. TAS names of the reference
  rocks agree with their rock types; for example BIR-1 and BHVO-2 →
  basalt, RGM-1 and the JR rhyolites → rhyolite, OKUM → komatiite, JP-1,
  JP-2 and UB-N → "TAS not applicable (ultramafic rock)". Plutonic rocks
  get volcanic TAS names, as expected; use the plutonic diagrams for them.

- **Iron split (0.17.0).**
  - Hand check: for a basalt with anhydrous SiO2 = 49 and Na2O + K2O = 3,
    Le Maitre (1976, volcanic) gives Ox = 0.658 and Fe2O3/FeO = 0.519; the
    app gives 0.519. Synthetic points in each TAS field receive the
    Middlemost (1989) ratio of Table I, including the alkali rules for
    tephrite/basanite and foidite.
  - Mass balance: FeO + 0.8998 Fe2O3 equals the total iron for every
    sample (largest difference below 10⁻¹² wt%).
  - Comparison with measured FeO and Fe2O3 in the global database of Gard
    et al. (2019) (40,000 volcanic and 40,000 plutonic rocks with both
    values, totals 95–102 %, duplicates removed). Measured Fe³⁺/Fe(total):
    median 0.31 (volcanic) and 0.33 (plutonic). Median error of the
    predicted Fe³⁺/Fe(total):

    | Method | Volcanic: bias | Volcanic: abs. error | Fresh volcanic (LOI < 1 %): abs. error | Plutonic: abs. error |
    |---|---|---|---|---|
    | Fixed 0.15 | −0.17 | 0.17 | 0.15 | 0.18 |
    | Le Maitre (1976), volcanic | +0.07 | 0.13 | 0.15 | 0.15 |
    | Le Maitre (1976), plutonic | +0.00 | 0.11 | 0.11 | 0.11 |
    | Middlemost (1989) | −0.11 | 0.12 | 0.10 | — |

    No method predicts the ratio of a single sample well: measured ratios
    scatter widely (interquartile range 0.20–0.47), mostly through
    alteration. Report the method used, and measure FeO where the result
    depends on it.
  - The CIPW norm, the IUGS names (nephelinite test), Frost and Frost
    (2008), Agrawal et al. (2008) and Verma et al. (2006) were run with each
    method on the example sets without error.

- **Mineral modes (0.25.0).**
  - Albarède (1995, Table 5.16): a komatiitic liquid as a mixture of
    olivine, clinopyroxene and garnet (seven components). Book: x₀ =
    (0.210, 0.267, 0.442), λ = 0.0188, x = (0.200, 0.235, 0.564). App:
    x₀ = (0.210, 0.267, 0.442), λ = 0.0188, x = (0.201, 0.235, 0.564)
    (the book rounds the intermediate values).
  - Synthetic partly serpentinised harzburgite with a known mode (olivine
    40, orthopyroxene 15, clinopyroxene 3, spinel 2, serpentine 38,
    magnetite 2 %): recovered exactly, also when 3 % of the mass is left
    out of the analysis (normalisation) and without H2O.
  - Brucite added to the default set: condition number 5180, ±1σ above
    100 % — the warning appears. Default set: condition number 27, ±1σ
    0.2–1.6 %.
  - 92 fully serpentinised peridotites (H2O or LOI > 11 wt%) of the global
    database (Gard et al. 2019): serpentine + magnetite + spinel +
    clinopyroxene give median modes 87, 9, 2 and 1 %. With the default set
    (olivine and orthopyroxene included) olivine comes out negative in
    almost every sample: the page then warns that a mineral is absent.
    Ideal Mg-serpentine carries no iron, so magnetite is an upper limit;
    use measured serpentine compositions for better values.

- **Hydrogen generation (0.26.0).**
  - Equations against hand calculation: 300 °C and 500 bar → 75.60
    (Eq. 3); 300 °C without pressure → 119.67 (Eq. 4); 350 °C → 88.30
    (Eq. 5); 450 °C → 0. Correction factor of the paper's example (60 %
    olivine, 40 % orthopyroxene) → 0.88. 1 km² × 100 m, 3200 kg/m³,
    C = 0.88, RH2 = 100 → GH2 = 5.632 × 10⁷ kg.
  - From depth: 7.5 km, 23 °C + 30 °C/km → 248 °C; hydrostatic 736 bar →
    86.6 mmol/kg; lithostatic (3000 kg/m³) 2207 bar → 194.0 mmol/kg.
  - Synthetic rocks with known answers (`tools/synthetic_h2_test.py`):
    six rocks (dunite, harzburgite, lherzolite, partly serpentinised
    harzburgite, serpentinite, websterite) mixed from the ideal minerals
    and written as a lab would (Fe2O3t, LOI), with Temperature and Depth
    columns. The app recovers every mode within 0.01 wt%, every C within
    10⁻⁴ and every RH2 exactly; the Depth column gives the same results
    as the Temperature column; the volumetric total of a 10 km² × 3 km
    body equals the hand sum. Also checked through the full app.
  - Already generated (0.27.0), synthetic rocks: S from water and from
    the serpentine mode both equal the known serpentine content (0, 0, 0,
    0.38, 0.88, 0) within 0.001; H₂ = S × 227 (86.3 and 199.8 mmol/kg),
    low and high = S × 150 and S × 300; the websterite gets the pyroxenite
    note. Water rules: H2O+ = 6.5 is used before LOI = 12 (H₂ = 113.5);
    LOI 10 − CO2 2.2 = 7.8 (H₂ = 136.2); a basalt gets no value.
  - Already generated, ultramafic example set: JP-1 0.16 (37 mmol/kg),
    JP-2 0.01 (2), UB-N serpentinite 0.80 from water and 0.82 from the mode
    (182 and 187 mmol/kg, range 120–248); the komatiite and the
    hornblendite are not ultramafic by the screening and get no value.
  - Full app (test harness): the tab opens without data, with the example
    set and with the synthetic set; a warning appears when the yield is
    outside the low–high range. A crash found in this test (the example
    cards were drawn twice on the page without data) was fixed before
    release.
  - Per sample tab with the ultramafic example set: fresh peridotites
    JP-1 and JP-2 give C = 0.77 and 0.80; the serpentinite UB-N gives
    C = 0.11, because its olivine has already reacted.
  - Worked example of the paper (Giles Complex: 32 000 km³, 0–20 km,
    area 1600 km², C = 0.8, 23 °C + 30 °C/km, 100 m intervals). The paper
    gives 2.24 × 10¹⁵ kg before the 0.01 reacted fraction. The app gives
    1.12 × 10¹³ kg with lithostatic pressure at 3000 kg/m³ and 6.06 × 10¹²
    kg with hydrostatic pressure. The paper does not give the density or
    how P was calculated. The lithostatic result times 200 (the number of
    100 m intervals) is 2.25 × 10¹⁵ kg, which matches the paper. This
    suggests that the paper multiplied the rate of each interval by the
    mass of the whole body. The app follows the method as written (each
    interval with its own mass). Check this with the author before you
    compare your totals with the paper's.

### 10.1 Sources of the example datasets

The start page and the *Example datasets* menu offer eight sets. Two are
synthetic and are labelled *Synthetic* in the app: the quick tour
(`geochem/example_data.csv`) and the messy lab file
(`examples/geochem_test_30.xlsx`). The other six are **real rocks**:
international geochemical reference materials, taken from
`geochem/examples/reference_rocks.csv`.

- **USGS rocks** (BHVO-2, BCR-2, BIR-1, AGV-2, RGM-1, GSP-2, G-2, STM-1):
  certified or recommended values and information values from the USGS
  certificates of analysis, unchanged. MnO = Mn × 1.2912 where a
  certificate gives Mn in µg/g [App convention, oxide conversion]. The
  certificates give no LOI.
- **GSJ and other rocks** (JB-1a, JB-2, JB-3, JA-1, JA-2, JA-3, JR-1, JR-2,
  JR-3, JG-1a, JG-2, JG-3, JGb-1, JGb-2, JH-1, JP-1, JP-2, UB-N, OKUM): major
  elements, Cr and Ni from Mikuni et al. (2025, Table 1), who compiled them
  from Imai et al. (1995, 1999), Terashima et al. (1998) and the IAG and
  SARM certificates (as cited in Mikuni et al. 2025). LOI is the value
  measured by Mikuni et al. (2025) on their own powders; a negative LOI is a
  gain on ignition (oxidation of Fe²⁺).
- Empty cells mean that the source gives no value. No value was
  estimated or filled in.
- Rock types are those of the sources. *Group* (the colour in plots) is a
  simplified rock type, the broad class (volcanic, plutonic, ultramafic)
  or, for the basalt set, the tectonic setting: mid-ocean-ridge type
  (BIR-1, Iceland), ocean island (BHVO-2, Hawaii), continental flood basalt
  (BCR-2, Columbia River) and island arc (JB-2, Izu-Oshima; JB-3, Fuji).
  [App convention]
- Every row names its source in the *Reference* column.

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
- Lee C.-T.A., Brandon A.D., Norman M. (2003) Vanadium in peridotites as a
  proxy for paleo-fO2 during partial melting: prospects, limitations, and
  implications. Geochimica et Cosmochimica Acta 67, 3045–3064.
- Le Maitre R.W. (1976) Some problems of the projection of chemical data
  into mineralogical classifications. Contributions to Mineralogy and
  Petrology 56, 181–189. (iron split, section 3)
- Le Maitre R.W. (ed.) (2002) Igneous Rocks: A Classification and Glossary
  of Terms. Recommendations of the International Union of Geological
  Sciences Subcommission on the Systematics of Igneous Rocks, 2nd edition.
  Cambridge University Press, Cambridge. ISBN 978-0-521-66215-4
- Maniar P.D., Piccoli P.M. (1989) Tectonic discrimination of granitoids.
  Geological Society of America Bulletin 101, 635–643.
- Aitchison J., Egozcue J.J. (2005) Compositional data analysis: where are
  we and where should we be heading? Mathematical Geology 37, 829–850.
  (as cited in Rollinson and Pease 2021)
- Albarède F. (1995) Introduction to Geochemical Modeling. Cambridge
  University Press, Cambridge. (section 5.3: mineral modes by least
  squares with a closure condition; Table 5.16)
- Gard M., Hasterok D., Halpin J.A. (2019) Global whole-rock geochemical
  database compilation. Earth System Science Data 11, 1553–1566.
  doi:10.5194/essd-11-1553-2019 (test data for the iron split, version
  1.1.0 on Zenodo)
- Grant J.A. (1986) The isocon diagram — a simple solution to Gresens'
  equation for metasomatic alteration. Economic Geology 81, 1976–1982. (as
  cited in Grant 2005)
- Grant J.A. (2005) Isocon analysis: a brief review of the method and
  applications. Physics and Chemistry of the Earth 30, 997–1004.
  doi:10.1016/j.pce.2004.11.003
- Harker A. (1909) The Natural History of Igneous Rocks. Methuen, London.
  (as cited in Rollinson and Pease 2021)
- Middlemost E.A.K. (1989) Iron oxidation ratios, norms and the
  classification of volcanic rocks. Chemical Geology 77, 19–26.
- Salters V.J.M., Stracke A. (2004) Composition of the depleted mantle.
  Geochemistry, Geophysics, Geosystems 5, Q05B07. doi:10.1029/2003GC000597
- Saccani E. (2015) A new method of discriminating different types of
  post-Archean ophiolitic basalts and their tectonic significance using
  Th-Nb and Ce-Dy-Yb systematics. Geoscience Frontiers 6, 481–501.
  doi:10.1016/j.gsf.2014.03.006
- MacLean W.H., Barrett T.J. (1993) Lithogeochemical techniques using
  immobile elements. Journal of Geochemical Exploration 48, 109–133.
- Mikuni K., Ishikawa A., Sato R. (2025) Geochemical Journal 59(6),
  299–314. doi:10.2343/geochemj.GJ25017 (XRF module and the GSJ example
  rocks; full reference in the user manual, chapter 14)
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
- Albers E., Bach W., Pérez-Gussinyé M., McCammon C., Frederichs T.
  (2021) Serpentinization-driven H2 production from continental break-up
  to mid-ocean ridge spreading: unexpected high rates at the West Iberia
  margin. Frontiers in Earth Science 9, 673063. (as cited in Liu et al.
  2023)
- Klein F., Bach W., McCollom T.M. (2013) Compositional controls on
  hydrogen generation during serpentinization of ultramafic rocks. Lithos
  178, 55–69.
- Liu Z., Pérez-Gussinyé M., García-Pintado J., Mezri L., Bach W. (2023)
  Mantle serpentinization and associated hydrogen flux at North Atlantic
  magma-poor rifted margins. Geology 51, 284–289.
  https://doi.org/10.1130/G50722.1
- Rezaee R. (2025) Quantifying natural hydrogen generation rates and
  volumetric potential in onshore serpentinization. Geosciences 15, 112.
  https://doi.org/10.3390/geosciences15030112
- Rollinson H., Pease V. (2021) Using Geochemical Data: To Understand
  Geological Processes, 2nd edition. Cambridge University Press, Cambridge.
- Shand S.J. (1943) Eruptive Rocks. Their Genesis, Composition,
  Classification, and Their Relation to Ore-Deposits. John Wiley and Sons,
  New York.
- U.S. Geological Survey. Certificates of analysis of the geochemical
  reference materials AGV-2 (andesite), BCR-2 (basalt), BHVO-2 (basalt),
  BIR-1 (Icelandic basalt), G-2 (granite), GSP-2 (granodiorite), RGM-1
  (rhyolite) and STM-1 (syenite). USGS, Denver, Colorado. (example
  datasets)
- Snow J.E., Dick H.J.B. (1995) Pervasive magnesium loss by marine
  weathering of peridotite. Geochimica et Cosmochimica Acta 59, 4219–4235.
- Verma S.P., Rodríguez-Ríos R., González-Ramírez R. (2010) Statistical
  evaluation of classification diagrams for altered igneous rocks. Turkish
  Journal of Earth Sciences 19, 239–265. doi:10.3906/yer-0902-9
- Winchester J.A., Floyd P.A. (1977) Geochemical discrimination of
  different magma series and their differentiation products using immobile
  elements. Chemical Geology 20, 325–343. (as evaluated by Verma et al. 2010)
