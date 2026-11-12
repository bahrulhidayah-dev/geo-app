# Example files

All files are synthetic or published data, for learning and testing.

| File | Content |
|---|---|
| geochem_test_30.xlsx | 30 synthetic samples in 4 suites, with typical lab "problems" (units row, `<0.01`, `bdl`, `n.d.`, decimal comma, column-name variants). Sheet "Test guide" lists the expected results. |
| geochem_test_30_with_styles.xlsx | The same samples with Symbol, Colour and Size columns (GCDkit convention). |
| xrf_qc_test.xlsx | Synthetic XRF results with 8 reference-material rows and serpentinite/peridotite samples, for the XRF quality-control module. |
| xrf_intensities_example_mikuni2025.csv | Raw X-ray intensities, dilution factors and LOI of 26 reference materials and working standards from Mikuni et al. (2025) Geochemical Journal 59, 299-314 (Tables 1 and 3, CC BY 4.0), for "Calibration from intensities". |
| ../geochem/examples/reference_rocks.csv | 27 real reference rocks (USGS, GSJ, IAG, SARM) used by the app's example datasets. USGS rocks: USGS certificates (majors and traces). Others: Mikuni et al. (2025) Table 1 (majors, Cr, Ni, LOI). Sources in the file header and in the Reference column. |
| ../geochem/examples/hydrogen_tutorial.csv | Six synthetic peridotites, a serpentinite and a pyroxenite mixed from ideal minerals with known modes, with Temperature (°C), Depth (m) and Pressure (bar) columns. Used by the hydrogen generation tutorial (Documentation page); the expected results are listed there. |
| ../geochem/examples/hydrogen_synthetic_20.csv | Hydrogen practice set: 20 synthetic rocks in four scenarios (serpentinization series, protolith types, drill core 1–12 km, special cases with carbonate, brucite, H2O+ and a basalt). Made by `tools/make_hydrogen_examples.py`; expected results in the hydrogen tutorial, chapter 11. |
| layout_and_units_example.xlsx | The example samples in a "difficult" lab layout: two title rows above the column names, a running number in the first column, sample names in the second, REE in ppb, column names with units. Use it to try Data > Column setup (column names on row 3, sample name = Lab ID, rock type = Lithology, locality = Area). |
