# GeoChem App

A free, open-source web app for whole-rock geochemistry (XRF and ICP data),
following Janoušek et al. (2006). Version 0.14.0.
Developed by Bahrul Hidayah (bahrul.hidayah@gmail.com).

**Try it online:** https://geo-app-hidayah.streamlit.app (no installation needed).
Source code: https://github.com/bahrulhidayah-dev/geo-app

**User manual:** [docs/user-manual.md](docs/user-manual.md) (also inside the app:
top bar > Documentation). **Portable and online versions:**
[docs/deployment.md](docs/deployment.md). **Architecture, data flow and
workflows:** [docs/architecture.md](docs/architecture.md). Changes: [CHANGELOG.md](CHANGELOG.md). How to cite:
[CITATION.cff](CITATION.cff) and the About page.

## Features

- Load CSV or Excel files. Values such as `<0.01`, `n.d.` and `bdl`, decimal
  commas, units rows and empty rows are handled and reported.
- Column names such as `SiO2 (wt%)`, `Fe2O3T` or `La_ppm` are recognised.
- Dashboard with TAS, AFM and spider diagrams plus a sample map and table.
- Diagram catalogue (31 diagrams) with boundaries taken unchanged from
  Janoušek et al. (2006) templates: TAS (IUGS), Middlemost plutonic TAS, Pearce 1996
  Nb/Y-Zr/Ti, Jensen, AFM, Peccerillo and Taylor, Miyashiro, Hastie Co-Th,
  Shand, Frost and Frost 2008, Pearce et al. 1984, Whalen et al. 1987,
  Martin 1986, Pearce 2008 (Th/Yb, TiO2/Yb), Saccani 2015, Shervais,
  Pearce and Cann, Meschede, Wood, Paulick et al. 2006; stage 2: R1-R2
  volcanic and plutonic (De la Roche et al. 1980), Batchelor and Bowden 1985,
  Agrawal et al. 2008, Verma et al. 2006, Ohta and Arai 2007 (F-M-W); Saccani 2015
  (Ce/Yb-Dy/Yb and Dy-Yb), drawn from the coordinates in the paper; Deschamps et al.
  2013 (LOI x 10 - SiO2 - sum of oxides; LOI vs SiO2 and MgO) for serpentinites.
- CIPW norm (Hutchison 1974, 1975; ported from Janoušek et al. 2006) with download.
- Top bar with Documentation (full user manual with screenshots),
  References, About, and the language (Indonesian, English, Japanese) and
  theme (light, dark or system) menus; the session is kept when the page
  reloads.
- Plot appearance: fonts, field-label orientation, tick-label angle, y-axis
  title orientation, line widths, figure size, grid.
- Automatic field names for every sample in classification diagrams.
- REE, multi-element and crust/sediment spider diagrams with all 35
  normalisation sets of Janoušek et al. (2006) (chondrite, primitive mantle, N-MORB, E-MORB, OIB ...).
- Units read from column names or a units row and converted (ppb, ppm, wt%);
  Column setup for any lab layout: header row, sample name, rock type,
  locality, group, and the meaning and unit of each column (save and reuse).
- Variation diagrams: Harker (SiO2) or MgO plates of all major oxides,
  anhydrous or as measured, with optional trace elements and iso-Mg# and
  olivine lines.
- Free XY plot and free ternary plot (any three components, sums of
  columns, factors such as Rb/30), group statistics, calculated values (FeOt, Mg#, anhydrous
  oxides).
- Symbols and colours per group (colour, symbol, size, filled or open), used by
  every diagram; saved and loaded as CSV. Per-sample Symbol, Colour and Size
  columns in the data file are read as in Janoušek et al. (2006).
- Figure export as PNG, SVG or PDF in a white publication style. Files are only
  created when a download button is clicked.
- Optional module (Settings > Optional modules): XRF quality control after
  Mikuni et al. (2025). Reference-material QC plots (deviation % and measured vs
  reference), accuracy (their Eq. 7), a library of 26 reference materials
  (their Table 1, CC BY 4.0) and an iron check for ultramafic rocks
  (T-Fe2O3 without Ca-Mg matrix correction; effect on Mg#).
  It also builds XRF calibration lines from raw glass-bead intensities
  (their Eqs. 1-8) with an optional matrix correction for T-Fe2O3 (Ca and Mg by
  default), and quantifies the unknowns on the as-received basis. Checked
  against the paper: with their SciTokyo_Day1 intensities the app gives
  R2 = 0.99967 and accuracy = 0.077 wt% for T-Fe2O3, and GP13 8.92 -> 8.40 wt%
  (paper: same values). The paper's data set is included as an example.

- Project files (`.geochem`: data plus all settings) to save, send and reopen
  an analysis; on the desktop and portable versions a work folder with
  `data`, `exports` and `projects` subfolders and one-click saving of figures
  and tables.
- Three ways to share: online (Streamlit Community Cloud), portable Windows
  ZIP with Python included, or from the source code. The online version shows
  a privacy note and has a maintenance mode switched on through Secrets
  (see [docs/deployment.md](docs/deployment.md)).

## Install and run

No installation: use the portable Windows ZIP or the online version
(see [docs/deployment.md](docs/deployment.md)).

From the source code (Python 3.12 or newer):

```
cd geo-app
python -m venv .venv
.venv\Scripts\activate              (Windows; macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
streamlit run app.py
```

## Project layout

```
app.py                     user interface (top bar, pages, sidebar, dashboard)
.streamlit/config.toml     colours and app settings
geochem/data.py            reading, cleaning and recognising columns
geochem/calc.py            geochemical recalculations
geochem/plotting.py        plotting engine (classification, ternary, spider)
geochem/symbols.py         symbols, colours and sizes per group
geochem/norms.py           CIPW norm
geochem/i18n.py            interface text in Indonesian, English and Japanese
geochem/catalog.py         diagram catalogue: axis formulas, categories, references
geochem/xrfqc.py           XRF quality control (Mikuni et al. 2025)
geochem/xrfcal.py          XRF calibration from raw intensities, matrix correction
geochem/reference_materials.csv  reference values of 26 RMs (Mikuni et al. 2025)
geochem/docs.py            manual, references and about pages
docs/user-manual.md        user manual (docs/img: screenshots)
docs/deployment.md         portable and online versions, release checklist
docs/architecture.md       design, data flow from file to figure, workflows
docs/diagrams/             sources of the architecture and flow charts
tools/portable/            portable Windows build (build_portable.bat, launcher)
examples/                  example data files (synthetic and published)
LICENSE                    GNU GPL v3.0
.devcontainer/             settings for editing in GitHub Codespaces (added by Streamlit)
geochem/diagrams/gcdkit/   boundary geometry converted from the templates of Janoušek et al. (2006)
tools/gcdkit_import.py     converter from the R templates (Janoušek et al. 2006) to JSON
geochem/diagrams/*.json    spider-plot normalizing values
geochem/example_data.csv   synthetic test data with known answers
```

## References

- Diagram boundaries: Janoušek et al. (2006), GPL >= 2; every diagram page
  lists its original reference.

- Janoušek V., Farrow C. M., Erban V. (2006) Interpretation of whole-rock
  geochemical data in igneous geochemistry: introducing Geochemical Data
  Toolkit (GCDkit). Journal of Petrology 47(6), 1255-1259.
  https://doi.org/10.1093/petrology/egl013
- TAS: Le Bas M.J. et al. (1986) Journal of Petrology 27, 745-750. Field
  coordinates as compiled in pyrolite (BSD-3).
- AFM: Irvine T.N., Baragar W.R.A. (1971) Canadian Journal of Earth Sciences 8,
  523-548. Boundary coordinates from GeoplotR (P. Vermeesch, GPL-3).
- Chondrite: McDonough W.F., Sun S.-s. (1995) Chemical Geology 120, 223-253.
- Primitive mantle: Sun S.-s., McDonough W.F. (1989) Geological Society Special
  Publication 42, 313-345.
- XRF QC: Mikuni K., Ishikawa A., Sato R. (2025) Accurate determination of
  whole-rock major element composition of ultramafic rocks through X-ray
  fluorescence spectrometry. Geochemical Journal 59(6), 299-314.
  doi:10.2343/geochemj.GJ25017 (CC BY 4.0).

## License

GNU General Public License v3.0 (GPL-3.0).
