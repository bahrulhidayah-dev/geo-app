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


def manual_text():
    return MANUAL.read_text(encoding="utf-8")


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
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return (f'<figure class="gc-fig"><img src="data:image/png;base64,{b64}" alt="{alt}"/>'
            f"<figcaption>{alt}</figcaption></figure>")


def embed_images(md):
    """Markdown image links -> inline <img> (base64), so the browser does not
    fetch separate files (download managers ignore them)."""
    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)",
                  lambda m: _img_tag(DOCS / m.group(2), m.group(1)), md)


# ---------------- references ----------------
GENERAL = [
    ("Software", "Janoušek V., Farrow C.M., Erban V. (2006) Interpretation of whole-rock "
     "geochemical data in igneous geochemistry: introducing Geochemical Data Toolkit "
     "(GCDkit). Journal of Petrology 47(6), 1255-1259. doi:10.1093/petrology/egl013"),
    ("CIPW norm", "Hutchison C.S. (1974) Laboratory Handbook of Petrographic Techniques. "
     "John Wiley and Sons, New York."),
    ("CIPW norm", "Hutchison C.S. (1975) The norm, its variations, their calculation and "
     "relationships. Schweizerische Mineralogische und Petrographische Mitteilungen 55, "
     "243-256."),
    ("Spider diagrams", "McDonough W.F., Sun S.-s. (1995) The composition of the Earth. "
     "Chemical Geology 120, 223-253. (CI chondrite)"),
    ("Spider diagrams", "Sun S.-s., McDonough W.F. (1989) Chemical and isotopic "
     "systematics of oceanic basalts: implications for mantle composition and processes. "
     "Geological Society, London, Special Publications 42, 313-345. (Primitive mantle)"),
    ("Colours", "Okabe M., Ito K. (2008) Color Universal Design (CUD): how to make "
     "figures and presentations that are friendly to colorblind people. "
     "jfly.uni-koeln.de/color (colour-blind safe palette)"),
    ("XRF module", xrfqc.CITATION + " (CC BY 4.0)"),
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
