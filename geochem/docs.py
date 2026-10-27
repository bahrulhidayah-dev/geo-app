# geochem/docs.py
# Documentation helpers: the user manual (docs/user-manual.md) split into
# chapters, screenshots embedded inline (no separate image downloads), and the
# reference list built from the diagram catalogue. Part of GeoChem App (GPL-3.0).

import base64
import re
from pathlib import Path

from . import catalog, xrfqc

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
MANUAL = DOCS / "user-manual.md"
# Documents shown on the Documentation page (title: file)
DOCUMENTS = {"User manual": MANUAL,
             "Scientific methods": DOCS / "methods.md",
             "Architecture and workflows": DOCS / "architecture.md",
             "Portable and online versions": DOCS / "deployment.md"}
CHANGELOG = ROOT / "CHANGELOG.md"

LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40" width="{s}" height="{s}">
<rect x="1" y="1" width="38" height="38" rx="10" fill="{bg}"/>
<path d="M20 8 L32 29 L8 29 Z" fill="none" stroke="{fg}" stroke-width="2.2" stroke-linejoin="round"/>
<path d="M14 18.5 L26 18.5 M11 24 L29 24" stroke="{fg}" stroke-width="1.2" opacity="0.55"/>
<circle cx="20" cy="21" r="2.6" fill="{dot}"/><circle cx="15" cy="26.5" r="1.9" fill="{dot}"/>
<circle cx="24.5" cy="15.5" r="1.6" fill="{dot}"/></svg>"""


def logo(size=34, dark=True):
    bg, fg, dot = (("#1C2A3A", "#8FD3BF", "#F2B66D") if dark else
                   ("#E3F1EC", "#2E8B74", "#D9822B"))
    return LOGO_SVG.format(s=size, bg=bg, fg=fg, dot=dot)


def _slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def manual_text(path=MANUAL):
    return Path(path).read_text(encoding="utf-8")


def chapters(md=None):
    """[(title, markdown)] split at level-2 headings. The text before the
    first chapter becomes 'Welcome'."""
    md = md or manual_text()
    parts = re.split(r"^## ", md, flags=re.M)
    intro = re.sub(r"^# .*\n", "", parts[0]).strip()
    out = [("Welcome", intro)] if intro else []
    for p in parts[1:]:
        title, _, body = p.partition("\n")
        out.append((title.strip(), body.strip()))
    return out


def _img_tag(path, alt):
    if not path.exists():
        return ""
    raw = path.read_bytes()
    b64 = base64.b64encode(raw).decode("ascii")
    style = ""
    if "diagrams" in path.parts:
        # charts are rendered at 2x: show them at their natural size
        # (never wider than the page), so tall charts do not become huge
        width = int.from_bytes(raw[16:20], "big") // 2       # PNG header
        style = f' style="width: {width}px"'
    return (f'<figure class="gc-fig"><img src="data:image/png;base64,{b64}" alt="{alt}"{style}/>'
            f"<figcaption>{alt}</figcaption></figure>")


def embed_images(md):
    """Markdown image links -> inline <img> (base64), so the browser does not
    fetch separate files (download managers ignore them)."""
    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)",
                  lambda m: _img_tag(DOCS / m.group(2), m.group(1)), md)


# ---------------- references ----------------
GENERAL = [
    ("Diagram templates and software", "Janoušek V., Farrow C.M., Erban V. (2006) Interpretation of whole-rock "
     "geochemical data in igneous geochemistry: introducing Geochemical Data Toolkit "
     "(GCDkit). Journal of Petrology 47(6), 1255-1259. "
     "https://doi.org/10.1093/petrology/egl013"),
    ("CIPW norm", "Hutchison C.S. (1974) Laboratory Handbook of Petrographic Techniques. "
     "John Wiley and Sons, New York."),
    ("CIPW norm", "Hutchison C.S. (1975) The norm, its variations, their calculation and "
     "relationships. Schweizerische Mineralogische und Petrographische Mitteilungen 55, "
     "243-256."),
    ("Iron split", "Le Maitre R.W. (1976) Some problems of the projection of chemical "
     "data into mineralogical classifications. Contributions to Mineralogy and Petrology "
     "56, 181-189. (FeO/(FeO + Fe2O3) from SiO2 and Na2O + K2O, volcanic and plutonic "
     "rocks)"),
    ("Iron split", "Middlemost E.A.K. (1989) Iron oxidation ratios, norms and the "
     "classification of volcanic rocks. Chemical Geology 77, 19-26. (standard "
     "Fe2O3/FeO ratios by TAS field)"),
    ("Iron split", "Gard M., Hasterok D., Halpin J.A. (2019) Global whole-rock "
     "geochemical database compilation. Earth System Science Data 11, 1553-1566. "
     "doi:10.5194/essd-11-1553-2019 (CC BY 4.0; used to test the iron split)"),
    ("Screening and naming", "Le Bas M.J., Le Maitre R.W., Streckeisen A., Zanettin B. "
     "(1986) A chemical classification of volcanic rocks based on the total alkali-silica "
     "diagram. Journal of Petrology 27, 745-750. (freshness limits H2O+ < 2 wt%, "
     "CO2 < 0.5 wt%; recalculation to 100 % volatile-free)"),
    ("Screening and naming", "Le Bas M.J., Le Maitre R.W., Woolley A.R. (1992) The "
     "construction of the Total Alkali-Silica chemical classification of volcanic rocks. "
     "Mineralogy and Petrology 46, 1-22."),
    ("Screening and naming", "Le Maitre R.W. (ed.) (2002) Igneous Rocks: A Classification "
     "and Glossary of Terms. Recommendations of the IUGS Subcommission on the Systematics "
     "of Igneous Rocks, 2nd edition. Cambridge University Press. (high-Mg rocks and "
     "nephelinites before TAS; iron partitioning)"),
    ("Screening and naming", "Le Bas M.J. (2000) IUGS reclassification of the high-Mg and "
     "picritic volcanic rocks. Journal of Petrology 41, 1467-1470. (as cited in "
     "Le Maitre et al. 2002)"),
    ("Screening and naming", "Le Bas M.J. (1989) Nephelinitic and basanitic rocks. Journal "
     "of Petrology 30, 1299-1312. (as cited in Le Maitre et al. 2002)"),
    ("Serpentinites and peridotites", "Niu Y. (2004) Bulk-rock major and trace element "
     "compositions of abyssal peridotites: implications for mantle melting, melt "
     "extraction and post-melting processes beneath mid-ocean ridges. Journal of "
     "Petrology 45, 2423-2458. (terrestrial and oceanic arrays, MgO deficit)"),
    ("Serpentinites and peridotites", "Snow J.E., Dick H.J.B. (1995) Pervasive magnesium "
     "loss by marine weathering of peridotite. Geochimica et Cosmochimica Acta 59, "
     "4219-4235."),
    ("Serpentinites and peridotites", "Deschamps F., Godard M., Guillot S., Hattori K. "
     "(2013) Geochemistry of subduction zone serpentinites: a review. Lithos 178, 96-127. "
     "doi:10.1016/j.lithos.2013.05.019 (Fe oxidation and Ca loss during serpentinization)"),
    ("Serpentinites and peridotites", "Hart S.R., Zindler A. (1986) In search of a "
     "bulk-Earth composition. Chemical Geology 57, 247-267. (terrestrial array; metal "
     "ratios)"),
    ("Variation diagrams", "Rollinson H., Pease V. (2021) Using Geochemical Data: To "
     "Understand Geological Processes, 2nd edition. Cambridge University Press. "
     "(Harker and MgO variation diagrams, Mg#, interpretation of trends, closure)"),
    ("Variation diagrams", "Harker A. (1909) The Natural History of Igneous Rocks. "
     "Methuen, London. (as cited in Rollinson and Pease 2021)"),
    ("Reliability of diagrams", "Verma S.P., Rodríguez-Ríos R., González-Ramírez R. (2010) "
     "Statistical evaluation of classification diagrams for altered igneous rocks. "
     "Turkish Journal of Earth Sciences 19, 239-265. doi:10.3906/yer-0902-9"),
    ("Reliability of diagrams", "Winchester J.A., Floyd P.A. (1977) Geochemical "
     "discrimination of different magma series and their differentiation products using "
     "immobile elements. Chemical Geology 20, 325-343."),
    ("Spider diagrams", "McDonough W.F., Sun S.-s. (1995) The composition of the Earth. "
     "Chemical Geology 120, 223-253. (CI chondrite)"),
    ("Spider diagrams", "35 sets of normalising values (chondrite, primitive mantle, "
     "MORB, OIB, continental crust, sediments ...) as compiled by Janoušek et al. (2006); the "
     "reference of each set is shown on the Spider diagrams page."),
    ("Spider diagrams", "Sun S.-s., McDonough W.F. (1989) Chemical and isotopic "
     "systematics of oceanic basalts: implications for mantle composition and processes. "
     "Geological Society, London, Special Publications 42, 313-345. (Primitive mantle)"),
    ("Colours", "Okabe M., Ito K. (2008) Color Universal Design (CUD): how to make "
     "figures and presentations that are friendly to colorblind people. "
     "jfly.uni-koeln.de/color (colour-blind safe palette)"),
    ("XRF module", xrfqc.CITATION + " (CC BY 4.0)"),
    ("Example datasets", "U.S. Geological Survey. Certificates of analysis of the "
     "geochemical reference materials AGV-2, BCR-2, BHVO-2, BIR-1, G-2, GSP-2, RGM-1 "
     "and STM-1. USGS, Denver, Colorado."),
    ("Example datasets", "Mikuni K., Ishikawa A., Sato R. (2025), Table 1 (CC BY 4.0): "
     "major elements, Cr and Ni of the GSJ, IAG and SARM reference rocks, compiled from "
     "Imai et al. (1995, 1999), Terashima et al. (1998) and the IAG and SARM "
     "certificates."),
]

LIBRARIES = [
    ("Streamlit", "web interface", "Apache-2.0"),
    ("pandas", "tables", "BSD-3-Clause"),
    ("NumPy", "numerical calculations", "BSD-3-Clause"),
    ("Matplotlib", "plots", "Matplotlib (PSF-based)"),
    ("openpyxl", "Excel files", "MIT"),
]


def diagram_references():
    """{category: [(diagram title, reference, GCDkit source)]}"""
    out = {}
    for d in catalog.DIAGRAMS:
        out.setdefault(d["category"], []).append(
            (d["title"], d["reference"], d.get("source", "")))
    return {c: out[c] for c in catalog.CATEGORIES if c in out}


def references_text():
    lines = ["GeoChem App - references", ""]
    for cat, rows in diagram_references().items():
        lines += [f"[{cat}]"] + [f"- {r}" for _, r, _ in rows] + [""]
    lines += ["[Other]"] + [f"- {r}" for _, r in GENERAL]
    return "\n".join(lines) + "\n"
