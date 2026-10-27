# Changelog

All notable changes to GeoChem App. Versions follow MAJOR.MINOR.PATCH.

## 0.23.0 - 2026-10-27

- **V - MgO melting curves (Lee et al. 2003)**, a new diagram in
  Ultramafic rocks: residue curves for fractional melting of spinel
  peridotite at 1.5 GPa from FMQ-3 to FMQ+2, with 10 % melting steps.
  The curves are calculated from the paper's equations and Table 1 by the
  new developer script `tools/lee2003_vmgo.py`. 34 diagrams.
- Glossary: the diagram and "Oxygen fugacity (fO2) and buffers".
- Scientific methods: the calculation, the conventions (temperature for
  FMQ to NNO, interpolation of Table 1) and the comparison with Fig. 4A,
  including the larger difference of the reduced curves.

## 0.22.0 - 2026-10-27

- **Trace elements vs Yb in serpentinites (Deschamps et al. 2013)**, a
  plate of 11 log-log panels in Ultramafic rocks: Ti, La/Yb and the
  fluid-mobile elements Li, B, Cs, Sr, Ba, U, Pb, As and Sb against Yb,
  with primitive-mantle (McDonough and Sun 1995) and depleted-mantle
  (Salters and Stracke 2004) reference points. 33 diagrams.
- Reference points (minerals, mantle compositions) are now drawn above the
  data so they stay visible.
- Tested with 289 serpentinites of the global database.
- Glossary, Scientific methods, References, user manual.

## 0.21.0 - 2026-10-27

- **Fe redox in serpentinites (Paulick et al. 2006)**, a new diagram in
  Ultramafic rocks with three panels: Fe2O3 vs measured FeO (magnetite
  ratio line and lines of equal total iron), Fe2O3 vs LOI and
  Fe3+/Fe(total) vs LOI (magnetite = 2/3). Only samples with FeO and Fe2O3
  both measured are plotted; split iron is never used. 32 diagrams.
- Tested with 134 serpentinites of the global database (Gard et al. 2019).
- Glossary entry; Scientific methods (section 5 and section 10); user
  manual diagram list.

## 0.20.0 - 2026-10-27

- **Stage B starts: two LOI diagrams for serpentinites (Deschamps et al.
  2013)** in the category Ultramafic rocks:
  - (LOI x 10) - SiO2 - sum of oxides (Fig. 3a), with the SiO2/Sum = 0.81
    line of 899 serpentinites and lines of equal LOI;
  - LOI - SiO2 and LOI - MgO (Figs. 4d, 4f).
  Oxides on the anhydrous basis of the paper (including Cr2O3 and NiO);
  ideal mineral points for brucite, serpentine, talc, forsterite and
  enstatite. The catalogue now has 31 diagrams.
- Glossary entries; Scientific methods (section 5 and a hand check for UB-N
  in section 10); user manual diagram list.

## 0.19.0 - 2026-10-27

- **Two new diagrams for ophiolitic basalts (Saccani 2015)**, the second
  step after NbN - ThN, for rock types that overlap there:
  - (Ce/Yb)N - (Dy/Yb)N: G-MORB (garnet-influenced) vs N-MORB;
  - DyN - YbN: boninite vs island-arc tholeiite (IAT).
  Separation lines from the coordinates in the paper (sections 5.2 and
  5.3); chondrite values of Sun and McDonough (1989). The catalogue now has
  29 diagrams.
- Glossary entries, Scientific methods (section 5 and a hand check in
  section 10), user manual diagram list.

## 0.18.1 - 2026-10-27

- **Bar chart of sample counts per field** in the Results tab of every
  diagram with named fields: number and percentage of samples, sorted by
  count; samples without a field (unclassified, no data, "TAS not
  applicable") in grey at the bottom. PNG, SVG and PDF downloads. For plates
  with several panels, *Count samples in* chooses the panel. Idea from
  GeoPyTool (Yu et al. 2018).

## 0.18.0 - 2026-10-27

- **Glossary** (version 1), a new document on the Documentation page for
  beginners: 65 entries in plain English on data and chemistry terms,
  petrology terms, plot types and every one of the 27 catalogue diagrams
  (what it shows, when to use it and when not, original reference).
- Search box on the Glossary: type a word, diagram or author to see every
  matching entry.
- **Open in the glossary** button in the *Scientific basis* tab of every
  diagram.
- Short definitions in the **?** help of key settings (anhydrous basis,
  ultramafic threshold, iron split, spider normalisation), in English,
  Indonesian and Japanese.

## 0.17.1 - 2026-10-27

- **New default iron split: Le Maitre (1976), volcanic equation**, as
  recommended by Le Bas et al. (1986) when only total iron is given (was:
  fixed Fe3+/Fe(total) = 0.15). Choose the plutonic equation for plutonic
  rocks.
- This changes the CIPW norm, the nephelinite test and Verma et al. (2006)
  for samples with total iron only, also in projects saved before this
  version. Choose *Fixed Fe3+/Fe(total) ratio* in Settings to get the
  earlier results. Measured FeO and Fe2O3 are still used as they are.

## 0.17.0 - 2026-10-27

- **Iron split methods** (Settings → Iron split when only total iron is
  measured), used by the CIPW norm, the nephelinite test before TAS and
  Verma et al. (2006):
  - fixed Fe3+/Fe(total) ratio (as before, default 0.15);
  - Le Maitre (1976), volcanic or plutonic equation (recommended by Le Bas
    et al. 1986);
  - Middlemost (1989), standard Fe2O3/FeO ratio for each TAS field.
- New switch **Also replace measured FeO and Fe2O3** to standardise every
  sample (Middlemost 1989).
- The note under the CIPW norm table names the method used.
- New module `geochem/iron.py`.
- **Fix:** in files that mix iron forms (some rows with FeO and Fe2O3,
  others with total iron only), the total iron of the second group was left
  out of the anhydrous sum, which raised their anhydrous SiO2 and could
  change their TAS field. Iron is now counted once per sample. Files with
  one iron form give the same results as before.
- Scientific methods: section 3 rewritten (formulas, conventions, sources);
  section 10: hand checks and a test against 80,000 analyses with measured
  FeO and Fe2O3 (Gard et al. 2019). References page: new category Iron
  split.

## 0.16.1 - 2026-10-27

- **Legend no longer hides samples.** New default legend position
  *Automatic (avoids the data)*: eight places inside the plot are tried and
  the one that covers the fewest samples, field names and boundary lines is
  kept. If every place covers samples, the legend goes below the plot.
- New legend position **Below the plot** (in columns, under the x axis);
  keys of numbered labels follow below it.
- New option **Background behind the legend** (on by default): a box in the
  plot colour for a legend inside the plot.
- Sample labels and the legend share one obstacle check in the plotting
  engine.

## 0.16.0 - 2026-10-22

- **Example datasets**: eight sets to explore the app, as cards on the
  start page and in a new **Example datasets** menu in the left panel:
  quick tour (synthetic), volcanic rocks, granitoids, plutonic rocks,
  basalts from different tectonic settings, ultramafic rocks and
  serpentinite, all reference rocks, and a messy lab file (synthetic).
- The real sets are 27 international reference rocks: USGS certificates
  (majors and traces) and Mikuni et al. (2025) Table 1 (GSJ and other rocks;
  majors, Cr, Ni, LOI). New file `geochem/examples/reference_rocks.csv`.
- A loaded example shows its description and sources on the Dashboard and
  is coloured by its Group column.
- Scientific methods: section 10.1 (sources of the example data). Manual:
  chapter 2. References page: new category Example datasets.

## 0.15.2 - 2026-10-22

- The app opens in English (was Indonesian). English is first in the
  language menu.

## 0.15.1 - 2026-10-21

- New page **What's new** (changelog): latest version on top, earlier
  versions folded. Opened from the link "What's new · version" at the bottom
  of the left panel, above the developer credit, and from the About page.
  Only version numbers are shown; release dates stay in this file.

## 0.15.0 - 2026-10-21

- Overlapping text in diagrams:
  - Sample labels are placed automatically to avoid other labels, points,
    field names, the legend and the plot edge, with a leader line when
    needed (Plot appearance → Sample labels: Auto-arrange, Fixed or
    Numbers with a key).
  - All sample labels have a thin outline in the background colour.
  - Field names can be shown as numbers with a key below the plot.
  - TAS: "Trachyte / Trachydacite" moved to the middle of its field.
- Scientific methods: chapter 7 and the conventions table (chapter 9).
  Manual: chapter 12.

## 0.14.0 - 2026-10-21

- New page **Variation diagrams** (Plots menu): Harker diagrams (SiO2 on the
  x axis) or MgO variation diagrams, one panel per major oxide, in one plate.
  - Basis anhydrous (default) or as measured.
  - 2, 3 or 4 panels per row; all panels share the x range.
  - Optional trace elements (as measured); Ni and Cr suggested for MgO
    diagrams.
  - On MgO diagrams: iso-Mg# lines (85–95) and the olivine line on the FeOt
    panel (Deschamps et al. 2013), each Auto, Always or Off.
  - Plotted values as CSV; scientific basis with references; choices saved
    in project files.
- Sources: Rollinson and Pease (2021) for the choice of x axis, Mg#, the
  reading of trends and the closure caveat; Harker (1909) as cited there.
- Scientific methods: variation diagrams (chapter 5), new app conventions
  (chapter 9) and tests (chapter 10). Manual: chapter 9.

## 0.13.0 - 2026-10-21

Checks from the Stage A and B literature review (`reference/stage_AB_findings.md`).

- **TAS names follow the IUGS order** (Le Maitre et al. 2002, p. 34).
  "High-Mg" rocks (boninite, komatiite, meimechite, picrite) are named
  first, then nephelinite and melanephelinite (CIPW norm), then the TAS
  field. Samples whose Rock type or Group names an ultramafic rock get
  "TAS not applicable". Before this change a serpentinite was named, for
  example, foidite. The TAS Results tab shows the IUGS name, the TAS field
  and the freshness for TAS.
- **Freshness for TAS** (Le Bas et al. 1986): H2O+ > 2 wt% or
  CO2 > 0.5 wt% is suspect; LOI > 2.5 wt% is used as a proxy; the rule is
  withdrawn for high-Mg rocks.
- **H2O+ and CO2 columns are recognised.** They are used by the freshness
  check, the CIPW norm (as in Janoušek et al. 2006) and the carbonate correction of F-M-W.
- **F-M-W (Ohta and Arai 2007)**: missing or zero TiO2, CaO, Na2O and K2O
  are replaced by 0.005 wt%, as in the paper. Before, such samples were
  lost. A warning explains that Ca loss during serpentinization raises W.
- **Ultramafic samples** (anhydrous MgO threshold in Settings, or Rock type
  or Group) are detected everywhere, not only in the XRF module. There are
  warnings when FeO was not measured (CIPW norm, Verma et al. 2006).
- **Paulick diagram**: oceanic array and abyssal peridotite field of
  Niu (2004) added. New column "MgO deficit vs terrestrial array (%)" for
  ultramafic samples.
- Reliability notes from Verma et al. (2010) for Nb/Y - Zr/Ti (Pearce 1996)
  and Co - Th (Hastie et al. 2007).
- Manual: chapters 6, 7, 13 and 17 updated.
- New document **Scientific methods** (Documentation page). It describes
  every reading, screening, calculation, classification and plotting step
  with its source. Steps from papers, steps from Janoušek et al. (2006) and the app's own
  conventions are marked separately, and all app conventions are listed in
  one table.
- Citation style: the source of diagram templates, the CIPW norm, normalising
  values and conventions is now cited as Janoušek et al. (2006) everywhere
  (interface in all three languages, diagram notes, documents), with the
  full reference and DOI in the reference lists.
- References page: new sources added (Le Bas et al. 1986, 1992; Le Maitre
  et al. 2002; Le Bas 1989, 2000; Niu 2004; Snow and Dick 1995; Deschamps
  et al. 2013; Hart and Zindler 1986; Verma et al. 2010; Winchester and
  Floyd 1977).

## 0.12.0 - 2026-10-21

- New page **Ternary plot** (Plots menu): any three components, each the sum
  of one or more columns with an optional factor (for example Rb/30, Ta*3).
  Values are closed to 100 % with the apex order of Janoušek et al. (2006) (A left, B top,
  C right); optional 20 % grid lines; samples with missing or negative values
  are left out and listed. Plotted values as CSV; scientific basis with
  references. FeOt is calculated when it is not in the file. Choices are
  saved in project files.
- Manual: ternary plot section in chapter 9.

## 0.11.0 - 2026-10-20

- Project page. Project files (`.geochem`) hold the data file and the whole
  session (column setup, symbols, appearance, settings, grouping, diagram,
  spider normalisation, XRF intensities): save, send and open again; works
  online too.
- Work folder (desktop and portable): choose a folder; the app creates
  `data`, `exports` and `projects`, lists data files and projects to open
  with one click, saves figures (PNG, SVG, PDF) and tables straight into
  `exports`, and remembers the folder and recent folders.
- Manual: new chapter 15, Projects and the work folder.

## 0.10.0 - 2026-10-20

- Units: read from the column names (`La (ppb)`, `Cr_ppm`, `ng/g` ...) or a
  units row, and converted (elements to ppm, oxides to wt%). Conversions are
  listed in Data check. Before, ppb values were read as ppm.
- Column setup (Data page): header row for files with title rows, sample
  name column, rock type, locality and group roles, and the meaning and unit
  of every column; save and load the setup as JSON.
- Spider diagrams: all 35 normalisation sets compiled by Janoušek et al. (2006) (REE,
  multi-element, crust and sediments), with the values shown in Scientific
  basis. The default primitive mantle now uses the values of Janoušek et al. (2006) (Cs 0.0079,
  Pb 0.071 ppm; previously 0.032 and 0.185).
- Fix: a file without recognised oxide columns no longer stops the Data page.
- New example: `examples/layout_and_units_example.xlsx`.

## 0.9.1 - 2026-10-20

- The app is online: https://geo-app-hidayah.streamlit.app (source code:
  https://github.com/bahrulhidayah-dev/geo-app). Links added to the About
  page, README, manual and CITATION.cff.
- Maintenance mode for the online version, switched on and off in
  Streamlit Cloud > Settings > Secrets (`MAINTENANCE`,
  `MAINTENANCE_MESSAGE`, `MAINTENANCE_KEY`), with developer access by key.
- Fix: after an update on Streamlit Cloud, changed `geochem/` modules are
  now reloaded automatically (before, the online app could keep old modules
  in memory and fail until it was rebooted).
- Fix: online, the top bar no longer overlaps the Streamlit Cloud toolbar
  (Share, GitHub ...).
- New document: architecture and workflows (design principles, layers,
  data flow from file to figure, how a diagram is defined, user and
  developer workflows), with five charts. The Documentation page now
  offers the user manual, this document and the deployment guide.
- Documentation: GitHub Desktop workflow (commit, push, pull), maintenance
  mode, online troubleshooting, and the real repository name.

## 0.9.0 - 2026-10-19

- Portable Windows version: `tools/portable/build_portable.bat` builds a ZIP
  with Python included (no installation, no internet needed by the user).
- Ready for online deployment (Streamlit Community Cloud): pinned library
  versions, a bounded session memory, and a privacy note in the online
  version. Guide: `docs/deployment.md`.
- LICENSE file (GPL-3.0), `.gitignore`, and an `examples/` folder.
- Fix: the CIPW cache now uses the data content as key.

## 0.8.0 - 2026-10-19

- New top bar with Documentation, References, About, language and theme menus.
- Complete user manual inside the app (and in `docs/user-manual.md`), with
  screenshots.
- References page: the source of every diagram, calculation and data set.
- About page: version, license, how to cite and acknowledgements.
- Mg# from the XRF calibration is now on the same 0-100 scale as elsewhere.

## 0.7.0 - 2026-10-19

- XRF calibration from raw glass-bead intensities (Mikuni et al. 2025,
  Eqs. 1-8), with optional matrix correction of T-Fe2O3 (Ca and Mg by
  default), R2 and accuracy per oxide, and quantification of the unknowns.
- The paper's SciTokyo_Day1 intensities are included as an example; the app
  reproduces the published values.
- Quantified samples can be opened directly in all diagrams.

## 0.6.0 - 2026-10-19

- Optional XRF quality-control module: reference-material QC (deviation %,
  measured vs reference, accuracy), library of 26 reference materials,
  ultramafic iron check with the effect on Mg#.
- Cr2O3 and NiO columns are recognised.

## 0.5.0

- Stage 2 of the diagram catalogue: 27 diagrams from Janoušek et al. (2006), including
  R1-R2, Batchelor and Bowden, Agrawal et al. (2008), Verma et al. (2006),
  Ohta and Arai (2007) and Paulick et al. (2006).
- CIPW norm (Hutchison 1974, 1975).
- Interface in Indonesian, English and Japanese; light, dark or system theme.
- Plot appearance settings (fonts, label orientation, line widths, size).

## 0.4.0 and earlier

- Stage 1 diagram catalogue converted from the templates of Janoušek et al. (2006).
- Symbols and colours per group, legend position, style columns from the
  data file (convention of Janoušek et al. 2006).
- Dashboard, data cleaning and data check, spider diagrams, XY plots,
  statistics, figure export (PNG, SVG, PDF) without automatic downloads.
- Windows desktop shortcut.
