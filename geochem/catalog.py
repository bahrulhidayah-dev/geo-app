# geochem/catalog.py
# The diagram catalogue: what each diagram plots (axis formulas), where it
# belongs (category), and its scientific reference. Boundary geometry comes
# from GCDkit 6.3 templates (Janousek et al. 2006; GPL), converted to JSON by
# tools/gcdkit_import.py and stored in geochem/diagrams/gcdkit/.
# Part of GeoChem App (GPL-3.0).

import json
from pathlib import Path

import numpy as np
import pandas as pd

from . import calc, iron, norms
from .calc import milli, mol, need

GEOM_DIR = Path(__file__).parent / "diagrams" / "gcdkit"

CATEGORIES = ["Classification", "Magma series", "Granitoids",
              "Basalts and ophiolites", "Ultramafic rocks", "Weathering and alteration"]
DISCRIMINANTS = json.loads((GEOM_DIR / "discriminants.json").read_text())


# ---------- axis formulas (each takes the standardized data table) ----------
def anh(df, settings):
    """Major oxides on an anhydrous basis when the setting asks for it."""
    if settings.get("tas_recalc", True):
        a, _ = calc.anhydrous(df)
        out = df.copy()
        for c in a.columns:
            out[c] = a[c]
        return out
    return df


def acnk(df):
    return mol(df, "Al2O3") / (mol(df, "CaO") + mol(df, "Na2O") + mol(df, "K2O"))


def ank(df):
    return mol(df, "Al2O3") / (mol(df, "Na2O") + mol(df, "K2O"))


def asi_frost(df):
    p = milli(df, "P2O5").fillna(0) if "P2O5" in df else 0
    return milli(df, "Al2O3") / (2 * (milli(df, "CaO") - 1.67 * p)
                                 + milli(df, "Na2O") + milli(df, "K2O"))


def ga_al(df):
    # 10000*Ga/Al with Al in ppm (Al2O3 wt% x 5292.5)
    return 10000 * need(df, "Ga") / (need(df, "Al2O3") * 5292.5)


def agpaitic(df):
    return (mol(df, "Na2O") + mol(df, "K2O")) / mol(df, "Al2O3")


def r1(df):
    """R1 = 4Si - 11(Na + K) - 2(Fe(total as Fe2+) + Ti), millications."""
    return (4 * milli(df, "SiO2") - 11 * (milli(df, "Na2O") + milli(df, "K2O"))
            - 2 * (milli(df, "FeOt") + milli(df, "TiO2")))


def r2(df):
    """R2 = 6Ca + 2Mg + Al, millications."""
    return 6 * milli(df, "CaO") + 2 * milli(df, "MgO") + milli(df, "Al2O3")


def _norm_cache(df, settings):
    # key from the data themselves (not id(df), which Python may reuse)
    key = ("cipw", int(pd.util.hash_pandas_object(df, index=True).sum()),
           tuple(df.columns), iron.spec(settings))
    cache = settings.setdefault("_cache", {})
    if key not in cache:
        cache.clear()
        cache[key] = norms.cipw(df, iron.spec(settings))[0]
    return cache[key]


def fssi(df, settings):
    """Feldspathoid silica-saturation index (Frost and Frost 2008), CIPW norm."""
    n = _norm_cache(df, settings)
    return (n["Q"] - (n["Lc"] + 2 * (n["Ne"] + n["Kp"]))) / 100


def ai_frost(df):
    """Alkalinity index AI = Al - (Na + K), millications / 1000."""
    return (milli(df, "Al2O3") - (milli(df, "Na2O") + milli(df, "K2O"))) / 1000


def _with_split_iron(df, settings):
    feo, fe2o3, _ = norms.iron_for_norm(df, iron.spec(settings))
    out = df.copy()
    out["FeO"], out["Fe2O3"] = feo, fe2o3
    return out


def anh_split_iron(df, settings):
    """Anhydrous majors (SiO2 ... P2O5, with FeO and Fe2O3) summed to 100 %."""
    d = _with_split_iron(df, settings)
    cols = ["SiO2", "TiO2", "Al2O3", "Fe2O3", "FeO", "MnO", "MgO", "CaO",
            "Na2O", "K2O", "P2O5"]
    for c in cols:
        if c not in d:
            raise calc.MissingData(c)
    t = d[cols].sum(axis=1, min_count=len(cols))
    return d[cols].div(t, axis=0) * 100


def expr_panel(did, i, axis):
    """Discriminant function copied from the GCDkit template (Agrawal, Verma)."""
    src = DISCRIMINANTS[did][i][axis]

    def f(df, settings):
        a = anh_split_iron(df, settings) if "A(" in src else None
        W = lambda name: need(df, name)                     # noqa: E731
        A = lambda name: a[name]                            # noqa: E731
        with np.errstate(divide="ignore", invalid="ignore"):
            return eval(src, {"np": np, "W": W, "A": A, "__builtins__": {}})
    return f


OHTA_ZERO = 0.005      # wt%, replacement for zeros (Ohta and Arai 2007)


def ohta_replaced(df):
    """Number of samples in which Ohta and Arai's 0.005 wt% replacement was
    used for TiO2, CaO (silicate), Na2O or K2O."""
    n = pd.Series(0, index=df.index)
    for c in ("TiO2", "Na2O", "K2O", "CaO"):
        if c in df:
            n += (df[c].isna() | (df[c] <= 0)).astype(int)
    return int((n > 0).sum())


def ohta_arai(df):
    """F, M, W apices of Ohta and Arai (2007), as coded in GCDkit."""
    ox = {}
    for c in ("SiO2", "TiO2", "Al2O3", "MgO", "CaO", "Na2O", "K2O"):
        ox[c] = need(df, c)
    ox["Fe2O3t"] = need(df, "FeOt") * 1.111
    p2o5 = df["P2O5"].fillna(0) if "P2O5" in df else 0
    co2 = df["CO2"].fillna(0) if "CO2" in df else 0
    m_cao, m_p2o5, m_co2 = 56.0774, 141.9445, 44.0098
    apatite = (p2o5 / m_p2o5) / 3
    ox["CaO_corr"] = ox["CaO"] - (co2 / m_co2) * m_cao - apatite * m_cao * 10
    t = pd.DataFrame(ox)
    t = t[["SiO2", "TiO2", "Al2O3", "Fe2O3t", "MgO", "CaO_corr", "Na2O", "K2O"]]
    # Ohta and Arai (2007, section 2): missing values and rounding zeros are
    # replaced by 0.005 wt%, because log(0) is undefined. GCDkit sets them to 0
    # instead, which loses the sample. The four main oxides must be measured.
    minor = ["TiO2", "CaO_corr", "Na2O", "K2O"]
    t[minor] = t[minor].where(t[minor] > 0, OHTA_ZERO)
    t = t.div(t.sum(axis=1), axis=0) * 100
    L = {c: np.log(t[c].where(t[c] > 0)) for c in t}
    M = np.exp(-0.395 * L["SiO2"] + 0.206 * L["TiO2"] - 0.316 * L["Al2O3"]
               + 0.160 * L["Fe2O3t"] + 0.246 * L["MgO"] + 0.368 * L["CaO_corr"]
               + 0.073 * L["Na2O"] - 0.342 * L["K2O"] + 2.266)
    F = np.exp(0.191 * L["SiO2"] - 0.397 * L["TiO2"] + 0.020 * L["Al2O3"]
               - 0.375 * L["Fe2O3t"] - 0.243 * L["MgO"] + 0.079 * L["CaO_corr"]
               + 0.392 * L["Na2O"] + 0.333 * L["K2O"] - 0.892)
    W_ = np.exp(0.203 * L["SiO2"] + 0.191 * L["TiO2"] + 0.296 * L["Al2O3"]
                + 0.215 * L["Fe2O3t"] - 0.002 * L["MgO"] - 0.448 * L["CaO_corr"]
                - 0.464 * L["Na2O"] + 0.008 * L["K2O"] - 1.374)
    return F, M, W_


def B(x=None, y=None, xlab=None, ylab=None, basis=None):
    return {"kind": "binary", "x": x, "y": y, "xlab": xlab, "ylab": ylab,
            "basis": basis}


def T(a, b, c, labels):
    """Ternary: a = bottom-left apex, b = top, c = bottom-right (GCDkit order)."""
    return {"kind": "ternary", "a": a, "b": b, "c": c, "apices": labels}


DIAGRAMS = [
    # ----------------------------- classification -----------------------------
    dict(id="TAS", title="TAS (Le Bas et al. 1986)", category="Classification",
         scope="Volcanic rocks", year=1986, iugs=True,
         panels=[B(lambda d, s: anh(d, s)["SiO2"],
                   lambda d, s: anh(d, s)["Na2O"] + anh(d, s)["K2O"],
                   "SiO2 (wt%)", "Na2O + K2O (wt%)", "anhydrous")],
         reference="Le Bas M.J., Le Maitre R.W., Streckeisen A., Zanettin B. (1986) "
                   "A chemical classification of volcanic rocks based on the total "
                   "alkali-silica diagram. Journal of Petrology 27, 745-750. "
                   "Naming order (high-Mg rocks and nephelinites first): Le Maitre R.W. "
                   "(ed.) (2002) Igneous Rocks: A Classification and Glossary of Terms, "
                   "2nd ed. Cambridge University Press.",
         notes="IUGS-recommended classification of fresh volcanic rocks. The dashed "
               "line separates alkaline and subalkaline series (Irvine and "
               "Baragar 1971).\n\n"
               "**Checks before TAS (Le Maitre et al. 2002, p. 34).** The Results "
               "tab first tests the IUGS 'high-Mg' rules (wt%, anhydrous): "
               "SiO2 > 52, MgO > 8, TiO2 < 0.5 = boninite; 30 < SiO2 < 52, "
               "MgO > 18, Na2O + K2O < 2 = komatiite (TiO2 < 1) or meimechite "
               "(TiO2 > 1); 30 < SiO2 < 52, MgO > 12, Na2O + K2O < 3 = picrite. "
               "Samples in the foidite and basanite/tephrite fields are tested "
               "with the CIPW norm: ne > 20 % = nephelinite; ne < 20 % with "
               "ab < 5 % = melanephelinite. Samples whose Rock type is "
               "serpentinite, peridotite, dunite, harzburgite or lherzolite are "
               "marked 'TAS not applicable'.\n\n"
               "**Freshness (Le Bas et al. 1986).** Analyses with H2O+ > 2 wt% or "
               "CO2 > 0.5 wt% are suspect; LOI > 2.5 wt% is used as a proxy when "
               "H2O+ and CO2 were not measured. The rule is withdrawn for "
               "high-Mg rocks. TAS is not meant for plutonic, cumulate, "
               "metasomatised or strongly altered rocks."),
    dict(id="MiddlemostPlut", title="TAS for plutonic rocks (Middlemost 1985)",
         category="Classification", scope="Plutonic rocks", year=1985,
         panels=[B(lambda d, s: anh(d, s)["SiO2"],
                   lambda d, s: anh(d, s)["Na2O"] + anh(d, s)["K2O"],
                   "SiO2 (wt%)", "Na2O + K2O (wt%)", "anhydrous")],
         reference="Middlemost E.A.K. (1985) Magmas and Magmatic Rocks. Longman, London.",
         notes="Chemical names for plutonic rocks, the plutonic counterpart of TAS."),
    dict(id="Pearce1996", title="Nb/Y - Zr/Ti (Pearce 1996)", category="Classification",
         scope="Altered volcanic rocks", year=1996, field_log=(True, True),
         panels=[B(lambda d, s: need(d, "Nb") / need(d, "Y"),
                   lambda d, s: need(d, "Zr") / need(d, "Ti"), "Nb/Y", "Zr/Ti")],
         reference="Pearce J.A. (1996) A user's guide to basalt discrimination "
                   "diagrams. In: Wyman D.A. (ed.) Trace Element Geochemistry of "
                   "Volcanic Rocks. Geological Association of Canada Short Course "
                   "Notes 12, 79-113. After Winchester and Floyd (1977).",
         notes="Uses immobile elements, so it is often used for altered and "
               "metamorphosed volcanic rocks where TAS fails. Ti may come from "
               "TiO2.\n\n"
               "**Reliability.** Verma et al. (2010, Turkish Journal of Earth "
               "Sciences 19, 239-265) tested the original Winchester and Floyd "
               "(1977) Nb/Y - Zr/TiO2 diagram (not this Pearce 1996 version) "
               "with fresh volcanic rocks named by TAS and the CIPW norm. "
               "Correct names: alkali basalt 74 %, andesite 75 %, phonolite 76 %, "
               "but subalkaline basalt 32 %, basanite 30 %, trachyandesite 29 %, "
               "trachyte 30 %, dacite 25 %, rhyolite 17 %. Treat the field name "
               "as a guide, not a final name."),
    dict(id="Jensen", title="Jensen cation plot (Jensen 1976)",
         category="Classification", scope="Subalkaline volcanic rocks", year=1976,
         panels=[T(lambda d, s: milli(d, "Al2O3"),
                   lambda d, s: milli(d, "FeOt") + milli(d, "TiO2"),
                   lambda d, s: milli(d, "MgO"),
                   ("Al", "Fe(t) + Ti", "Mg"))],
         reference="Jensen L.S. (1976) A new cation plot for classifying subalkalic "
                   "volcanic rocks. Ontario Geological Survey Miscellaneous Paper 66. "
                   "Field boundaries after Rickwood (1989).",
         notes="Cation proportions. Separates komatiites, tholeiites and "
               "calc-alkaline rocks; popular for Archean greenstone belts."),
    # ----------------------------- magma series --------------------------------
    dict(id="AFM", title="AFM (Irvine and Baragar 1971)", category="Magma series",
         scope="Subalkaline rocks", year=1971,
         panels=[T(lambda d, s: need(d, "Na2O") + need(d, "K2O"),
                   lambda d, s: need(d, "FeOt"),
                   lambda d, s: need(d, "MgO"), ("A", "F", "M"))],
         reference="Irvine T.N., Baragar W.R.A. (1971) A guide to the chemical "
                   "classification of the common volcanic rocks. Canadian Journal "
                   "of Earth Sciences 8, 523-548.",
         notes="A = Na2O + K2O, F = FeOt, M = MgO (wt%)."),
    dict(id="PeceTaylor", title="SiO2 - K2O (Peccerillo and Taylor 1976)",
         category="Magma series", scope="Subalkaline volcanic rocks", year=1976,
         panels=[B(lambda d, s: need(d, "SiO2"), lambda d, s: need(d, "K2O"),
                   "SiO2 (wt%)", "K2O (wt%)")],
         reference="Peccerillo A., Taylor S.R. (1976) Geochemistry of Eocene "
                   "calc-alkaline volcanic rocks from the Kastamonu area, Northern "
                   "Turkey. Contributions to Mineralogy and Petrology 58, 63-81.",
         notes="Boundaries extrapolated after Rickwood (1989), as in Janoušek et al. (2006)."),
    dict(id="Miyashiro", title="SiO2 - FeOt/MgO (Miyashiro 1974)",
         category="Magma series", scope="Subalkaline rocks", year=1974,
         panels=[B(lambda d, s: need(d, "SiO2"),
                   lambda d, s: need(d, "FeOt") / need(d, "MgO"),
                   "SiO2 (wt%)", "FeOt/MgO")],
         reference="Miyashiro A. (1974) Volcanic rock series in island arcs and "
                   "active continental margins. American Journal of Science 274, "
                   "321-355."),
    dict(id="Hastie", title="Co - Th (Hastie et al. 2007)", category="Magma series",
         scope="Altered arc volcanic rocks", year=2007, field_log=(False, True),
         panels=[B(lambda d, s: need(d, "Co"), lambda d, s: need(d, "Th"),
                   "Co (ppm)", "Th (ppm)")],
         reference="Hastie A.R., Kerr A.C., Pearce J.A., Mitchell S.F. (2007) "
                   "Classification of altered volcanic island arc rocks using "
                   "immobile trace elements: development of the Th-Co discrimination "
                   "diagram. Journal of Petrology 48, 2341-2357.",
         notes="Immobile-element replacement for SiO2-K2O in altered arc rocks. "
               "The Co axis runs from high to low.\n\n"
               "**Reliability.** Verma et al. (2010, Turkish Journal of Earth "
               "Sciences 19, 239-265) found a minimum misclassification of "
               "25-93 % for 7 of 14 rock-type and setting combinations. The "
               "diagram has only three rock-name regions; its main use is the "
               "series name (tholeiitic, calc-alkaline, high-K and shoshonitic), "
               "and only for rocks known to come from an arc."),
    # ----------------------------- granitoids ----------------------------------
    dict(id="Shand", title="A/CNK - A/NK (Shand 1943)", category="Granitoids",
         scope="Granitoids, felsic rocks", year=1943,
         panels=[B(lambda d, s: acnk(d), lambda d, s: ank(d),
                   "A/CNK (molar)", "A/NK (molar)")],
         reference="Shand S.J. (1943) Eruptive Rocks. John Wiley and Sons, New York. "
                   "Plot after Maniar and Piccoli (1989).",
         notes="A/CNK = Al2O3/(CaO+Na2O+K2O), A/NK = Al2O3/(Na2O+K2O), molar."),
    dict(id="Frost_2008", title="Frost and Frost (2008)", category="Granitoids",
         scope="Granitoids, feldspathic rocks", year=2008,
         panels=[B(lambda d, s: need(d, "SiO2"),
                   lambda d, s: need(d, "FeOt") / (need(d, "FeOt") + need(d, "MgO")),
                   "SiO2 (wt%)", "FeOt/(FeOt + MgO)"),
                 B(lambda d, s: need(d, "SiO2"),
                   lambda d, s: need(d, "Na2O") + need(d, "K2O") - need(d, "CaO"),
                   "SiO2 (wt%)", "MALI: Na2O + K2O - CaO (wt%)"),
                 B(lambda d, s: need(d, "SiO2"), lambda d, s: asi_frost(d),
                   "SiO2 (wt%)", "ASI"),
                 B(lambda d, s: fssi(d, s), lambda d, s: ai_frost(d),
                   "FSSI (CIPW norm)", "AI = Al - (Na + K) (molar)")],
         reference="Frost B.R., Frost C.D. (2008) A geochemical classification for "
                   "feldspathic igneous rocks. Journal of Petrology 49, 1955-1969.",
         notes="Fe-number, modified alkali-lime index (MALI), aluminium "
               "saturation index (ASI) and feldspathoid silica-saturation index "
               "(FSSI, from the CIPW norm)."),
    dict(id="PearceGranite", title="Pearce et al. (1984) granite discrimination",
         category="Granitoids", scope="Granitoids", year=1984,
         panels=[B(lambda d, s: need(d, "Y") + need(d, "Nb"), lambda d, s: need(d, "Rb"),
                   "Y + Nb (ppm)", "Rb (ppm)"),
                 B(lambda d, s: need(d, "Y"), lambda d, s: need(d, "Nb"),
                   "Y (ppm)", "Nb (ppm)"),
                 B(lambda d, s: need(d, "Yb") + need(d, "Ta"), lambda d, s: need(d, "Rb"),
                   "Yb + Ta (ppm)", "Rb (ppm)"),
                 B(lambda d, s: need(d, "Yb"), lambda d, s: need(d, "Ta"),
                   "Yb (ppm)", "Ta (ppm)")],
         reference="Pearce J.A., Harris N.B.W., Tindle A.G. (1984) Trace element "
                   "discrimination diagrams for the tectonic interpretation of "
                   "granitic rocks. Journal of Petrology 25, 956-983.",
         notes="VAG volcanic-arc, syn-COLG syn-collisional, WPG within-plate, "
               "ORG ocean-ridge granites."),
    dict(id="Whalen", title="A-type granites (Whalen et al. 1987)",
         category="Granitoids", scope="Granitoids", year=1987,
         panels=[B(lambda d, s: need(d, "Zr") + need(d, "Nb") + need(d, "Ce") + need(d, "Y"),
                   lambda d, s: need(d, "FeOt") / need(d, "MgO"), "Zr+Nb+Ce+Y (ppm)", "FeOt/MgO"),
                 B(lambda d, s: need(d, "Zr") + need(d, "Nb") + need(d, "Ce") + need(d, "Y"),
                   lambda d, s: (need(d, "Na2O") + need(d, "K2O")) / need(d, "CaO"),
                   "Zr+Nb+Ce+Y (ppm)", "(Na2O+K2O)/CaO"),
                 B(lambda d, s: ga_al(d), lambda d, s: need(d, "Na2O") + need(d, "K2O"),
                   "10000 Ga/Al", "Na2O + K2O (wt%)"),
                 B(lambda d, s: ga_al(d),
                   lambda d, s: (need(d, "Na2O") + need(d, "K2O")) / need(d, "CaO"),
                   "10000 Ga/Al", "(Na2O+K2O)/CaO"),
                 B(lambda d, s: ga_al(d), lambda d, s: need(d, "K2O") / need(d, "MgO"),
                   "10000 Ga/Al", "K2O/MgO"),
                 B(lambda d, s: ga_al(d), lambda d, s: need(d, "FeOt") / need(d, "MgO"),
                   "10000 Ga/Al", "FeOt/MgO"),
                 B(lambda d, s: ga_al(d), lambda d, s: need(d, "Zr"), "10000 Ga/Al", "Zr (ppm)"),
                 B(lambda d, s: ga_al(d), lambda d, s: need(d, "Nb"), "10000 Ga/Al", "Nb (ppm)"),
                 B(lambda d, s: ga_al(d), lambda d, s: need(d, "Ce"), "10000 Ga/Al", "Ce (ppm)"),
                 B(lambda d, s: ga_al(d), lambda d, s: need(d, "Y"), "10000 Ga/Al", "Y (ppm)"),
                 B(lambda d, s: ga_al(d), lambda d, s: need(d, "Zn"), "10000 Ga/Al", "Zn (ppm)"),
                 B(lambda d, s: ga_al(d), lambda d, s: agpaitic(d), "10000 Ga/Al",
                   "Agpaitic index")],
         reference="Whalen J.B., Currie K.L., Chappell B.W. (1987) A-type granites: "
                   "geochemical characteristics, discrimination and petrogenesis. "
                   "Contributions to Mineralogy and Petrology 95, 407-419.",
         notes="FG fractionated felsic granites, OTG unfractionated M-, I- and "
               "S-type granites, A = average A-type granite. Needs Ga for most panels."),
    dict(id="LaYb", title="YbN - LaN/YbN, TTG and adakite (Martin 1986)",
         category="Granitoids", scope="TTG, adakite, granitoids", year=1986,
         panels=[B(lambda d, s: need(d, "Yb") / 0.22,
                   lambda d, s: (need(d, "La") / 0.33) / (need(d, "Yb") / 0.22),
                   "YbN", "(La/Yb)N")],
         reference="Martin H. (1986) Effect of steeper Archean geothermal gradient on "
                   "geochemistry of subduction-zone magmas. Geology 14, 753-756.",
         notes="Chondrite values La 0.33, Yb 0.22 ppm, as in Janoušek et al. (2006)."),
    # ----------------------------- basalts / ophiolites -----------------------
    dict(id="PearceNbThYb", title="Nb/Yb - Th/Yb (Pearce 2008)",
         category="Basalts and ophiolites", scope="Basalts, ophiolites", year=2008,
         panels=[B(lambda d, s: need(d, "Nb") / need(d, "Yb"),
                   lambda d, s: need(d, "Th") / need(d, "Yb"), "Nb/Yb", "Th/Yb")],
         reference="Pearce J.A. (2008) Geochemical fingerprinting of oceanic basalts "
                   "with applications to ophiolite classification and the search for "
                   "Archean oceanic crust. Lithos 100, 14-48.",
         notes="The most used proxy for subduction input versus mantle source. "
               "Shaded band: MORB-OIB array."),
    dict(id="PearceNbTiYb", title="Nb/Yb - TiO2/Yb (Pearce 2008)",
         category="Basalts and ophiolites", scope="Basalts, ophiolites", year=2008,
         panels=[B(lambda d, s: need(d, "Nb") / need(d, "Yb"),
                   lambda d, s: need(d, "TiO2") / need(d, "Yb"), "Nb/Yb", "TiO2/Yb")],
         reference="Pearce J.A. (2008) Lithos 100, 14-48.",
         notes="Melting depth proxy: OIB array (deep) versus MORB array (shallow)."),
    dict(id="Saccani", title="NbN - ThN (Saccani 2015)",
         category="Basalts and ophiolites", scope="Ophiolitic basalts", year=2015,
         panels=[B(lambda d, s: need(d, "Nb") / 2.33, lambda d, s: need(d, "Th") / 0.12,
                   "NbN (N-MORB normalized)", "ThN (N-MORB normalized)")],
         reference="Saccani E. (2015) A new method of discriminating different types "
                   "of post-Archean ophiolitic basalts and their tectonic significance "
                   "using Th-Nb and Ce-Dy-Yb systematics. Geoscience Frontiers 6, 481-501.",
         notes="N-MORB values of Sun and McDonough (1989): Nb 2.33, Th 0.12 ppm."),
    # Saccani (2015) second-step diagrams. Chondrite values of Sun and McDonough
    # (1989): Ce 0.612, Dy 0.254, Yb 0.170 ppm (as listed in Rollinson and Pease
    # 2021, Table 4.7, column 1).
    dict(id="SaccaniCeDyYb", title="(Ce/Yb)N - (Dy/Yb)N, G-MORB vs N-MORB (Saccani 2015)",
         category="Basalts and ophiolites", scope="Ophiolitic basalts in the N-MORB field",
         year=2015,
         panels=[B(lambda d, s: (need(d, "Ce") / 0.612) / (need(d, "Yb") / 0.170),
                   lambda d, s: (need(d, "Dy") / 0.254) / (need(d, "Yb") / 0.170),
                   "(Ce/Yb)N (chondrite normalized)", "(Dy/Yb)N (chondrite normalized)")],
         reference="Saccani E. (2015) A new method of discriminating different types "
                   "of post-Archean ophiolitic basalts and their tectonic significance "
                   "using Th-Nb and Ce-Dy-Yb systematics. Geoscience Frontiers 6, 481-501.",
         notes="Second step after the NbN - ThN diagram (Saccani 2015): G-MORB "
               "(garnet-influenced MORB, typical of ocean-continent transition zones) "
               "and N-MORB plot together on Th-Nb, but G-MORB have higher MREE/HREE "
               "and LREE/HREE because garnet stayed in their mantle source. Use it "
               "for samples in the N-MORB field of the Th-Nb diagram. Separation line "
               "from (0.4, 1.5) to (2, 0.9) (section 5.2): 96 % of G-MORB and 99 % of "
               "N-MORB correctly classified in the paper; the dotted ends extend the "
               "line to the frame [App convention]. Chondrite values of Sun and "
               "McDonough (1989): Ce 0.612, Dy 0.254, Yb 0.170 ppm. The line was drawn "
               "by eye (Saccani 2015, section 7)."),
    dict(id="SaccaniDyYb", title="DyN - YbN, boninite vs IAT (Saccani 2015)",
         category="Basalts and ophiolites", scope="Ophiolitic basalts in the IAT field",
         year=2015,
         panels=[B(lambda d, s: need(d, "Dy") / 0.254, lambda d, s: need(d, "Yb") / 0.170,
                   "DyN (chondrite normalized)", "YbN (chondrite normalized)")],
         reference="Saccani E. (2015) A new method of discriminating different types "
                   "of post-Archean ophiolitic basalts and their tectonic significance "
                   "using Th-Nb and Ce-Dy-Yb systematics. Geoscience Frontiers 6, 481-501.",
         notes="Second step after the NbN - ThN diagram (Saccani 2015): island-arc "
               "tholeiites (IAT) and boninites plot together on Th-Nb. Boninites come "
               "from more depleted mantle or higher degrees of melting and have lower "
               "Dy and Yb. Use it for samples in the IAT field of the Th-Nb diagram. "
               "Separation line from (7, 25) to (9.5, 0) (section 5.3): 100 % of "
               "boninites and 99 % of IAT correctly classified in the paper. Chondrite "
               "values of Sun and McDonough (1989): Dy 0.254, Yb 0.170 ppm. The line was "
               "drawn by eye (Saccani 2015, section 7). For a full boninite name, also "
               "check the IUGS high-Mg rules (TAS Results tab)."),
    dict(id="Shervais", title="Ti - V (Shervais 1982)", category="Basalts and ophiolites",
         scope="Basalts", year=1982,
         panels=[B(lambda d, s: need(d, "Ti") / 1000, lambda d, s: need(d, "V"),
                   "Ti (ppm) / 1000", "V (ppm)")],
         reference="Shervais J.W. (1982) Ti-V plots and the petrogenesis of modern and "
                   "ophiolitic lavas. Earth and Planetary Science Letters 59, 101-118."),
    dict(id="Cann", title="Pearce and Cann (1973)", category="Basalts and ophiolites",
         scope="Basalts", year=1973,
         panels=[T(lambda d, s: need(d, "Zr"), lambda d, s: need(d, "Ti") / 100,
                   lambda d, s: 3 * need(d, "Y"), ("Zr", "Ti/100", "3 Y")),
                 T(lambda d, s: need(d, "Zr"), lambda d, s: need(d, "Ti") / 100,
                   lambda d, s: need(d, "Sr") / 2, ("Zr", "Ti/100", "Sr/2")),
                 B(lambda d, s: need(d, "Zr"), lambda d, s: need(d, "Ti"),
                   "Zr (ppm)", "Ti (ppm)")],
         reference="Pearce J.A., Cann J.R. (1973) Tectonic setting of basic volcanic "
                   "rocks determined using trace element analyses. Earth and Planetary "
                   "Science Letters 19, 290-300. Coordinates from Rollinson (1993).",
         notes="IAT island-arc tholeiite, CAB calc-alkaline basalt, MORB, WPB "
               "within-plate basalt."),
    dict(id="Meschede", title="Zr/4 - 2Nb - Y (Meschede 1986)",
         category="Basalts and ophiolites", scope="Basalts", year=1986,
         panels=[T(lambda d, s: need(d, "Zr") / 4, lambda d, s: 2 * need(d, "Nb"),
                   lambda d, s: need(d, "Y"), ("Zr/4", "2 Nb", "Y"))],
         reference="Meschede M. (1986) A method of discriminating between different "
                   "types of mid-ocean ridge basalts and continental tholeiites with "
                   "the Nb-Zr-Y diagram. Chemical Geology 56, 207-218.",
         notes="AI, AII within-plate alkali basalts; AII, C within-plate tholeiites; "
               "B E-MORB; D N-MORB; C, D volcanic-arc basalts."),
    dict(id="Wood", title="Th - Hf - Ta - Zr - Nb (Wood 1980)",
         category="Basalts and ophiolites", scope="Basalts", year=1980,
         panels=[T(lambda d, s: need(d, "Th"), lambda d, s: need(d, "Hf") / 3,
                   lambda d, s: need(d, "Ta"), ("Th", "Hf/3", "Ta")),
                 T(lambda d, s: need(d, "Th"), lambda d, s: need(d, "Hf") / 3,
                   lambda d, s: need(d, "Nb") / 16, ("Th", "Hf/3", "Nb/16")),
                 T(lambda d, s: need(d, "Th"), lambda d, s: need(d, "Zr") / 117,
                   lambda d, s: need(d, "Nb") / 16, ("Th", "Zr/117", "Nb/16"))],
         reference="Wood D.A. (1980) The application of a Th-Hf-Ta diagram to problems "
                   "of tectonomagmatic classification. Earth and Planetary Science "
                   "Letters 50, 11-30."),
    # ----------------------------- stage 2 ------------------------------------
    dict(id="LarocheVolc", title="R1 - R2 volcanic (De la Roche et al. 1980)",
         category="Classification", scope="Volcanic rocks", year=1980,
         panels=[B(lambda d, s: r1(d), lambda d, s: r2(d),
                   "R1 = 4Si - 11(Na + K) - 2(Fe + Ti)", "R2 = 6Ca + 2Mg + Al")],
         reference="De La Roche H., Leterrier J., Grandclaude P., Marchal M. (1980) "
                   "A classification of volcanic and plutonic rocks using R1R2-diagram "
                   "and major element analyses. Chemical Geology 29, 183-210.",
         notes="Millication proportions; total iron as Fe2+. Uses all major elements."),
    dict(id="LarochePlut", title="R1 - R2 plutonic (De la Roche et al. 1980)",
         category="Classification", scope="Plutonic rocks", year=1980,
         panels=[B(lambda d, s: r1(d), lambda d, s: r2(d),
                   "R1 = 4Si - 11(Na + K) - 2(Fe + Ti)", "R2 = 6Ca + 2Mg + Al")],
         reference="De La Roche H. et al. (1980) Chemical Geology 29, 183-210.",
         notes="Millication proportions; total iron as Fe2+."),
    dict(id="Batchelor", title="R1 - R2 tectonic setting (Batchelor and Bowden 1985)",
         category="Granitoids", scope="Granitoids", year=1985,
         panels=[B(lambda d, s: r1(d), lambda d, s: r2(d),
                   "R1 = 4Si - 11(Na + K) - 2(Fe + Ti)", "R2 = 6Ca + 2Mg + Al")],
         reference="Batchelor R.A., Bowden P. (1985) Petrogenetic interpretation of "
                   "granitoid rock series using multicationic parameters. Chemical "
                   "Geology 48, 43-55.",
         notes="1 mantle fractionates, 2 pre-plate collision, 3 post-collision "
               "uplift, 4 late-orogenic, 5 anorogenic, 6 syn-collision, "
               "7 post-orogenic."),
    dict(id="Agrawal", title="Agrawal et al. (2008), La-Sm-Yb-Nb-Th",
         category="Basalts and ophiolites", scope="Basic and ultrabasic rocks (SiO2 < 52)",
         year=2008, subset=lambda d, s: need(d, "SiO2") < 52,
         panels=[B(expr_panel("Agrawal", i, "x"), expr_panel("Agrawal", i, "y"),
                   "DF1", "DF2") for i in range(5)],
         reference="Agrawal S., Guevara M., Verma S.P. (2008) Tectonic discrimination "
                   "of basic and ultrabasic volcanic rocks through log-transformed "
                   "ratios of immobile trace elements. International Geology Review "
                   "50, 1057-1079.",
         notes="Discriminant functions of natural-log ratios to Th. Only samples "
               "with SiO2 < 52 wt% are plotted. IAB island arc, CRB continental "
               "rift, OIB ocean island, MORB mid-ocean ridge basalt."),
    dict(id="Verma", title="Verma et al. (2006), major elements",
         category="Basalts and ophiolites", scope="Basic and ultrabasic rocks (SiO2 < 52)",
         year=2006, subset=lambda d, s: anh_split_iron(d, s)["SiO2"] < 52,
         panels=[B(expr_panel("Verma", i, "x"), expr_panel("Verma", i, "y"),
                   "DF1", "DF2") for i in range(5)],
         reference="Verma S.P., Guevara M., Agrawal S. (2006) Discriminating four "
                   "tectonic settings: five new geochemical diagrams for basic and "
                   "ultrabasic volcanic rocks based on log-ratio transformation of "
                   "major-element data. Journal of Earth System Science 115, 485-528.",
         notes="Log ratios to SiO2 of anhydrous major elements with FeO and Fe2O3. "
               "When only total iron is measured it is split with the method chosen "
               "in Settings (fixed ratio, Le Maitre 1976 or Middlemost 1989). Only samples with SiO2 < 52 wt% are plotted. "
               "Not suitable for serpentinised rocks: serpentinization oxidises "
               "Fe2+ to Fe3+ (Deschamps et al. 2013; Paulick et al. 2006).",
         ultramafic_warning="Serpentinization raises Fe3+/Fe(total). Unless FeO "
                            "was measured, the iron split used here is not "
                            "reliable for these samples."),
    dict(id="OhtaArai", title="F - M - W weathering (Ohta and Arai 2007)",
         category="Weathering and alteration", scope="Igneous rocks, weathered",
         year=2007,
         panels=[T(lambda d, s: ohta_arai(d)[0], lambda d, s: ohta_arai(d)[1],
                   lambda d, s: ohta_arai(d)[2], ("F", "M", "W"))],
         reference="Ohta T., Arai H. (2007) Statistical empirical index of chemical "
                   "weathering in igneous rocks: a new tool for evaluating the degree "
                   "of weathering. Chemical Geology 240, 280-297.",
         notes="M mafic and F felsic igneous sources, W weathering intensity. "
               "Dashed: igneous trend; dotted: weathering trends of model rocks "
               "(Rhyo, Gra, Dac, And, Bas, Kom). CaO is corrected for apatite and "
               "carbonate. The eight oxides are closed to 100 %; missing or zero "
               "TiO2, CaO, Na2O and K2O are replaced by 0.005 wt%, as in the "
               "paper (section 2).\n\n"
               "**Limits (Ohta and Arai 2007, section 4).** Built from fresh and "
               "weathered igneous rocks. FeO-rich minerals (biotite, fayalite, "
               "chlorite) plot near W even when fresh, and the authors did not "
               "test metamorphic rocks.",
         ultramafic_warning="In ultramafic and serpentinised rocks, CaO and the "
                            "alkalis are close to zero. Loss of CaO during "
                            "serpentinization (Deschamps et al. 2013) alone can "
                            "raise W from about 14 to about 76 in a rock that "
                            "is not weathered. Do not read W as weathering for "
                            "these samples."),
    # ----------------------------- ultramafic ----------------------------------
    dict(id="Paulick", title="Al2O3/SiO2 - MgO/SiO2 (Paulick et al. 2006)",
         category="Ultramafic rocks", scope="Mantle peridotites, serpentinites",
         year=2006,
         panels=[B(lambda d, s: need(d, "Al2O3") / need(d, "SiO2"),
                   lambda d, s: need(d, "MgO") / need(d, "SiO2"),
                   "Al2O3/SiO2", "MgO/SiO2")],
         reference="Paulick H., Bach W., Godard M., De Hoog J.C.M., Suhr G., Harvey J. "
                   "(2006) Geochemistry of abyssal peridotites (Mid-Atlantic Ridge, "
                   "15 20'N, ODP Leg 209): implications for fluid/rock interaction in "
                   "slow spreading environments. Chemical Geology 234, 179-210. "
                   "Oceanic array and abyssal peridotite field added after Niu Y. (2004) "
                   "Journal of Petrology 45, 2423-2458.",
         notes="Grey band: the terrestrial array (melting trend; Jagoutz et al. "
               "1979), MgO/SiO2 = 1.107 - 2.598 Al2O3/SiO2 (Niu 2004). Dashed "
               "line: oceanic array of abyssal peridotites, MgO/SiO2 = 1.019 - "
               "2.596 Al2O3/SiO2, about 10 % lower MgO because of seafloor "
               "weathering (Niu 2004; Snow and Dick 1995). Dotted box: abyssal "
               "peridotites, 0.01 < Al2O3/SiO2 < 0.07 and 0.75 < MgO/SiO2 < 1.05 "
               "(Niu 2004). MgO/SiO2 about 1.2 is Fo90 olivine; dunites plot "
               "above the array, and MgO/SiO2 > 1.3 often means brucite "
               "(Paulick et al. 2006; Deschamps et al. 2013). Oxide ratios do "
               "not change with LOI.\n\n"
               "This diagram cannot tell abyssal, mantle-wedge and subducted "
               "serpentinites apart (Deschamps et al. 2013). The Data page "
               "gives the relative MgO deficit against the terrestrial array "
               "for ultramafic samples (assumes SiO2 and Al2O3 immobile, as "
               "Niu 2004).\n\n"
               "Niu Y. (2004) Journal of Petrology 45, 2423-2458. Snow J.E., "
               "Dick H.J.B. (1995) Geochimica et Cosmochimica Acta 59, "
               "4219-4235. Deschamps F. et al. (2013) Lithos 178, 96-127."),
]

BY_ID = {d["id"]: d for d in DIAGRAMS}
for _d in DIAGRAMS:
    _geo = json.loads((GEOM_DIR / f"{_d['id']}.json").read_text())
    n = _d.get("max_panels", len(_d["panels"]))
    _d["geometry"] = _geo["panels"][:n]
    _d["source"] = _geo["source"]
    _d.setdefault("field_log", (False, False))


def panel_data(diagram, i, df, settings):
    """Plot coordinates for panel i: DataFrame with x, y (binary) or
    a, b, c (ternary). Raises calc.MissingData if a column is missing."""
    p = diagram["panels"][i]
    if p["kind"] == "binary":
        out = pd.DataFrame({"x": p["x"](df, settings), "y": p["y"](df, settings)},
                           index=df.index)
    else:
        out = pd.DataFrame({"a": p["a"](df, settings), "b": p["b"](df, settings),
                            "c": p["c"](df, settings)}, index=df.index)
    if diagram.get("subset") is not None:
        keep = diagram["subset"](df, settings).fillna(False).astype(bool)
        out = out.where(keep)
    return out.replace([np.inf, -np.inf], np.nan)


def missing_columns(diagram, df, settings):
    """Names of missing columns per panel (empty list = panel can be drawn)."""
    out = []
    for i in range(len(diagram["panels"])):
        try:
            panel_data(diagram, i, df, settings)
            out.append([])
        except (calc.MissingData, KeyError) as e:
            out.append([str(e.args[0])])
    return out
