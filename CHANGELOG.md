# Changelog

All notable changes to GeoChem App. Versions follow MAJOR.MINOR.PATCH.

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
- Spider diagrams: all 35 normalisation sets of GCDkit 6.3 (REE,
  multi-element, crust and sediments), with the values shown in Scientific
  basis. The default primitive mantle now uses the GCDkit values (Cs 0.0079,
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

- Stage 2 of the diagram catalogue: 27 diagrams from GCDkit 6.3, including
  R1-R2, Batchelor and Bowden, Agrawal et al. (2008), Verma et al. (2006),
  Ohta and Arai (2007) and Paulick et al. (2006).
- CIPW norm (Hutchison 1974, 1975).
- Interface in Indonesian, English and Japanese; light, dark or system theme.
- Plot appearance settings (fonts, label orientation, line widths, size).

## 0.4.0 and earlier

- Stage 1 diagram catalogue converted from GCDkit 6.3 templates.
- Symbols and colours per group, legend position, style columns from the
  data file (GCDkit convention).
- Dashboard, data cleaning and data check, spider diagrams, XY plots,
  statistics, figure export (PNG, SVG, PDF) without automatic downloads.
- Windows desktop shortcut.
