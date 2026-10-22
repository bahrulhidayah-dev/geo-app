# geochem/examples.py
# Example datasets offered in the app, so that new users can explore every page.
# Most sets are real rocks: international geochemical reference materials
# (geochem/examples/reference_rocks.csv, sources in its header and in the
# Reference column). Two sets are synthetic and are labelled as such.
# Part of GeoChem App (GPL-3.0).

import io
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
ROOT = HERE.parent
REFERENCE_ROCKS = HERE / "examples" / "reference_rocks.csv"

# Broad rock class of each reference rock (used for colours in "All reference rocks")
CLASS = {"Basalt": "Volcanic", "Andesite": "Volcanic", "Rhyolite": "Volcanic",
         "Gabbro": "Plutonic", "Granitoid": "Plutonic", "Syenite": "Plutonic",
         "Hornblendite": "Plutonic", "Peridotite": "Ultramafic",
         "Serpentinite": "Ultramafic", "Komatiite": "Ultramafic"}

REF_NOTE = ("Real rocks: international geochemical reference materials. USGS rocks: USGS "
            "certificates of analysis (major and trace elements). GSJ and other rocks: "
            "Mikuni et al. (2025, Geochemical Journal 59, 299-314, Table 1, CC BY 4.0) "
            "and the references named there (major elements, Cr, Ni, LOI only). "
            "The source of every sample is in its Reference column.")

EXAMPLES = {
    "quick": dict(
        title="Quick tour: mixed rock suite",
        text="9 samples from basalt to rhyolite (within-plate, arc) and one serpentinite, "
             "with major and trace elements. A good first look at every page.",
        tags=["Synthetic", "Majors + traces"], icon=":material/explore:",
        file=HERE / "example_data.csv",
        note="Synthetic teaching data made for GeoChem App; not real analyses."),
    "volcanic": dict(
        title="Volcanic rocks: basalt to rhyolite",
        text="14 real reference rocks from Japan and the USA. Try TAS, AFM, "
             "K2O–SiO2 and the Harker diagrams.",
        tags=["Real rocks", "Majors; traces for USGS rocks"], icon=":material/volcano:",
        samples=["BIR-1", "BHVO-2", "JB-1a", "JB-2", "JB-3", "BCR-2", "JA-2", "AGV-2",
                 "JA-3", "JA-1", "JR-1", "JR-2", "JR-3", "RGM-1"], group="type"),
    "granitoid": dict(
        title="Granitoids",
        text="5 real granites and granodiorites (Japan, USA). Try Shand (A/CNK–A/NK), "
             "Frost et al. (2001, 2008) and Pearce et al. (1984); trace-element diagrams "
             "work for GSP-2 and G-2.",
        tags=["Real rocks", "Majors; traces for USGS rocks"], icon=":material/landscape:",
        samples=["JG-3", "GSP-2", "G-2", "JG-1a", "JG-2"], group="sample"),
    "plutonic": dict(
        title="Plutonic rocks: gabbro to syenite",
        text="9 real plutonic rocks: hornblendite, gabbros, granitoids and a peralkaline "
             "nepheline syenite. Try the plutonic classification diagrams.",
        tags=["Real rocks", "Majors; traces for USGS rocks"], icon=":material/terrain:",
        samples=["JH-1", "JGb-1", "JGb-2", "JG-3", "GSP-2", "G-2", "JG-1a", "JG-2",
                 "STM-1"], group="type"),
    "basalts": dict(
        title="Basalts from different tectonic settings",
        text="Mid-ocean-ridge type (Iceland), ocean island (Hawaii), continental flood "
             "basalt (Columbia River) and island arc (Izu-Oshima, Fuji). Compare them on "
             "spider and discrimination diagrams (traces for the three USGS basalts).",
        tags=["Real rocks", "Oceanic and arc"], icon=":material/water:",
        samples=["BIR-1", "BHVO-2", "BCR-2", "JB-2", "JB-3"], group="setting"),
    "ultramafic": dict(
        title="Ultramafic rocks and serpentinite",
        text="Dunite, lherzolite, serpentinite, komatiite and hornblendite (major "
             "elements, Cr, Ni, LOI). Try the MgO variation diagrams, the Paulick diagram "
             "and the ultramafic warnings.",
        tags=["Real rocks", "Majors, Cr, Ni"], icon=":material/diamond:",
        samples=["JP-1", "JP-2", "UB-N", "OKUM", "JH-1"], group="type"),
    "all": dict(
        title="All reference rocks",
        text="All 27 reference rocks, coloured as volcanic, plutonic or ultramafic.",
        tags=["Real rocks", "27 samples"], icon=":material/inventory_2:",
        samples=None, group="class"),
    "messy": dict(
        title="Messy lab file (data cleaning practice)",
        text="30 samples with typical lab problems: a units row, <0.01, bdl, n.d., "
             "decimal commas and different column names. See how the Data page cleans "
             "them.",
        tags=["Synthetic", "Excel file"], icon=":material/cleaning_services:",
        file=ROOT / "examples" / "geochem_test_30.xlsx",
        note="Synthetic test data with known answers (sheet 'Test guide')."),
}


def simple_type(rock_type):
    """'Basalt (olivine tholeiite)' -> 'Basalt'; 'Granodiorite' -> 'Granitoid'."""
    r = str(rock_type).lower()
    for key, name in (("basalt", "Basalt"), ("andesite", "Andesite"),
                      ("rhyolite", "Rhyolite"), ("granodiorite", "Granitoid"),
                      ("granite", "Granitoid"), ("gabbro", "Gabbro"),
                      ("syenite", "Syenite"), ("hornblendite", "Hornblendite"),
                      ("peridotite", "Peridotite"), ("serpentinite", "Serpentinite"),
                      ("komatiite", "Komatiite")):
        if key in r:
            return name
    return str(rock_type)


def reference_rocks():
    return pd.read_csv(REFERENCE_ROCKS, comment="#")


def available():
    """Keys of the example sets whose files exist (the 'messy' file may be absent)."""
    return [k for k, e in EXAMPLES.items()
            if "file" not in e or Path(e["file"]).exists()]


def load(key):
    """(file name, bytes) of an example set, ready to be read like an uploaded file."""
    e = EXAMPLES[key]
    if "file" in e:
        p = Path(e["file"])
        return p.name, p.read_bytes()
    df = reference_rocks()
    if e["samples"] is not None:
        df = df.set_index("Sample").loc[e["samples"]].reset_index()
    types = df["Rock type"].map(simple_type)
    group = {"type": types, "class": types.map(CLASS).fillna("Other"),
             "setting": df["Setting"], "sample": df["Rock type"]}[e["group"]]
    df.insert(1, "Group", group)
    df = df.dropna(axis=1, how="all")          # drop elements no sample has
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return f"example_{key}.csv", buf.getvalue().encode("utf-8")


def key_of(file_name):
    """Example key for a loaded file name, or None."""
    for k, e in EXAMPLES.items():
        if file_name == f"example_{k}.csv" or ("file" in e and Path(e["file"]).name == file_name):
            return k
    return None


def size(key):
    e = EXAMPLES[key]
    if e.get("samples"):
        return len(e["samples"])
    if key == "all":
        return len(reference_rocks())
    return None
