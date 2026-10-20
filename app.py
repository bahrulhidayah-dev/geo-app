# app.py
# GeoChem App: a free, web-based tool for whole-rock geochemistry,
# inspired by GCDkit (Janousek, Farrow and Erban 2006, J. Petrology 47: 1255-1259).
# Developed by Bahrul Hidayah. License: GPL-3.0
# Run with: streamlit run app.py

import os
import re
import uuid
from collections import OrderedDict
from pathlib import Path

import pandas as pd
import streamlit as st
from matplotlib.colors import to_hex

from geochem import calc, catalog, data, docs, norms, plotting, symbols, xrfcal, xrfqc
from geochem.i18n import LANGUAGES, t

APP_VERSION = "0.9.0"
DEVELOPER = "Bahrul Hidayah"
DEVELOPER_EMAIL = "bahrul.hidayah@gmail.com"
APP_URL = "https://geo-app-hidayah.streamlit.app"
REPO_URL = "https://github.com/bahrulhidayah-dev/geo-app"
HERE = Path(__file__).parent
EXAMPLE_FILE = HERE / "geochem" / "example_data.csv"
# Online deployment (Streamlit Community Cloud mounts apps under /mount/src,
# or set GEOCHEM_HOSTED=1 on other servers).
HOSTED = os.environ.get("GEOCHEM_HOSTED") == "1" or str(HERE).startswith("/mount/src")
NONE = "(none)"

st.set_page_config(page_title="GeoChem App", layout="wide",
                   initial_sidebar_state="expanded")

DIA = catalog.BY_ID
REE = plotting.load_diagram("spider_ree_chondrite_ms1995.json")
MULTI = plotting.load_diagram("spider_multi_pm_sm1989.json")

# ================= Session memory (survives a page reload) =================
# A theme change reloads the page. The data, settings and symbols are kept on
# this computer's app server under a key in the address (?s=...), so nothing
# has to be loaded again.
STATE_KEYS = ["dataset", "settings", "symbols", "lang", "group_col", "group_keep",
              "label_col", "diagram_id", "appearance", "theme_choice", "xrf_int"]


MAX_SESSIONS = 50          # remembered sessions on this server (oldest dropped)


@st.cache_resource
def _store():
    return OrderedDict()


token = st.query_params.get("s")
if not token:
    token = uuid.uuid4().hex[:12]
    st.query_params["s"] = token
if not st.session_state.get("_restored"):
    for k, v in _store().get(token, {}).items():
        st.session_state.setdefault(k, v)
    st.session_state["_restored"] = True

SETTINGS_DEFAULT = {"tas_recalc": True, "export_style": "publication",
                    "dpi": 300, "legend": "upper right", "palette": "Default",
                    "use_file_styles": True, "fe3_ratio": 0.15,
                    "xrf_qc": False, "um_mgo": 30.0, "qc_tol": 5.0}
settings = st.session_state.setdefault("settings", dict(SETTINGS_DEFAULT))
for _k, _v in SETTINGS_DEFAULT.items():
    settings.setdefault(_k, _v)
appearance = st.session_state.setdefault("appearance", dict(plotting.APPEARANCE_DEFAULT))
plotting.set_appearance(appearance)
st.session_state.setdefault("lang", "id")

# ================= Theme =================
THEME_CHOICES = ["System", "Light", "Dark"]
choice = st.session_state.setdefault("theme_choice", "System")
_active = st.context.theme.type or "dark"
DARK = _active == "dark"
SCREEN = "dark" if DARK else "light"

PAL = ({"bg": "#111827", "side": "#0D1420", "border": "#1F2A3D", "card": "#161E2B",
        "card_border": "#243049", "chip": "#18202E", "text": "#E8EDF5",
        "sub": "#8994A8", "head": "#6F7B90", "hover": "#18202E", "accent": "#4FB39A",
        "tag": "#1C2636", "tag_border": "#2A3750", "tag_text": "#B9C3D3"}
       if DARK else
       {"bg": "#F7F8FA", "side": "#EEF1F5", "border": "#DCE2EA", "card": "#FFFFFF",
        "card_border": "#DCE2EA", "chip": "#FFFFFF", "text": "#1B2333",
        "sub": "#5B6577", "head": "#6A7486", "hover": "#E4E9F0", "accent": "#2E8B74",
        "tag": "#F0F3F7", "tag_border": "#D5DCE5", "tag_text": "#3B4558"})

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&family=Noto+Sans+JP:wght@400;500;700&display=swap');
html, body, p, li, label, h1, h2, h3, h4, input, textarea, td, th,
[data-testid="stMarkdownContainer"], [data-testid="stMetricValue"],
[data-testid="stPageLink"] p, button p {{ font-family: 'Manrope', 'Noto Sans JP', sans-serif; }}
.block-container {{ padding-top: 3.2rem; padding-bottom: 2rem; max-width: 1500px; }}
[data-testid="stSidebar"] {{ background: {PAL['side']}; border-right: 1px solid {PAL['border']}; }}
[data-testid="stSidebar"] [data-testid="stPageLink"] a {{ border-radius: 8px; padding: 0.15rem 0.5rem; }}
[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {{ background: {PAL['hover']}; }}
[data-testid="stSidebar"] [data-testid="stPageLink"] {{ margin: -0.15rem 0; }}
[data-testid="stVerticalBlockBorderWrapper"] {{ background: {PAL['card']}; border-color: {PAL['card_border']} !important; border-radius: 14px; }}
.gc-brand {{ font-weight: 700; font-size: 1.15rem; letter-spacing: -0.01em; color: {PAL['text']}; }}
.gc-brand small {{ display:block; font-weight: 500; font-size: 0.78rem; color: {PAL['sub']}; margin-top: 2px; }}
.gc-header {{ display:flex; align-items: baseline; gap: 1.2rem; flex-wrap: wrap;
             padding: 0.2rem 0 0.9rem 0; border-bottom: 1px solid {PAL['border']}; margin-bottom: 1rem; }}
.gc-header h1 {{ font-size: 1.45rem; font-weight: 700; margin: 0; padding: 0; color: {PAL['text']}; }}
.gc-chip {{ font-size: 0.82rem; color: {PAL['sub']}; background: {PAL['chip']}; border: 1px solid {PAL['card_border']};
           border-radius: 999px; padding: 0.15rem 0.7rem; }}
.gc-chip b {{ color: {PAL['accent']}; font-weight: 600; }}
.gc-card-title {{ font-weight: 600; font-size: 1rem; color: {PAL['text']}; margin: 0; }}
.gc-card-sub {{ font-size: 0.78rem; color: {PAL['sub']}; margin: 0 0 0.3rem 0; }}
.gc-empty h2 {{ font-size: 2rem; font-weight: 700; letter-spacing: -0.02em; margin-bottom: 0.3rem; color: {PAL['text']}; }}
.gc-empty p {{ color: {PAL['sub']}; max-width: 62ch; }}
.gc-nav-head {{ font-size: 0.74rem; font-weight: 600; color: {PAL['head']}; margin: 0.9rem 0 0.2rem 0.5rem; }}
.gc-sub {{ color: {PAL['sub']}; font-size: 0.9rem; margin: -0.6rem 0 1rem 0; }}
.gc-meta {{ color: {PAL['sub']}; font-size: 0.82rem; margin: 0.1rem 0 0.6rem 0; }}
.gc-tag {{ display:inline-block; font-size: 0.72rem; color: {PAL['tag_text']}; background: {PAL['tag']};
          border: 1px solid {PAL['tag_border']}; border-radius: 6px; padding: 0 0.45rem; margin-right: 0.3rem; }}
.gc-tag.ok {{ color: {PAL['accent']}; }}
.gc-credit {{ font-size: 0.74rem; color: {PAL['sub']}; line-height: 1.45; margin-top: 1.2rem;
             padding-top: 0.7rem; border-top: 1px solid {PAL['border']}; }}
.gc-credit a {{ color: {PAL['sub']}; }}
.stButton button[kind="tertiary"], .stButton button[kind="primary"] {{ justify-content: flex-start;
          text-align: left; padding: 0.25rem 0.55rem; min-height: 2rem; }}
.stButton button[kind="tertiary"] p, .stButton button[kind="primary"] p {{ font-size: 0.88rem; text-align: left; }}
.stButton button[kind="tertiary"]:hover {{ background: {PAL['hover']}; }}
[data-testid="stIconMaterial"] {{ flex-shrink: 0; }}
[class*="st-key-dia_"] button div, [class*="st-key-dia_"] button span {{ justify-content: flex-start !important; }}
[class*="st-key-dia_"] {{ margin-bottom: -0.55rem; }}
header[data-testid="stHeader"] {{ background: transparent; }}
.st-key-gc_topbar {{ border-bottom: 1px solid {PAL['border']}; padding: 0 0 0.8rem 0;
          margin: -2.4rem 0 1.1rem 0; }}
[class*="st-key-doc_"] button div, [class*="st-key-doc_"] button span {{ justify-content: flex-start !important; }}
.st-key-doc_toc [class*="st-key-doc_"] {{ margin-bottom: -0.6rem; }}
.st-key-doc_body h2 {{ font-size: 1.55rem; font-weight: 700; }}
.st-key-doc_body h3 {{ font-size: 1.15rem; font-weight: 650; margin-top: 0.8rem; }}
.st-key-gc_topbar [data-testid="stPageLink"] a, .st-key-gc_topbar [data-testid="stPopover"] button {{
          border: 1px solid {PAL['card_border']}; border-radius: 999px; background: {PAL['chip']};
          padding: 0.18rem 0.75rem; min-height: 2.1rem; justify-content: center; }}
.st-key-gc_topbar [data-testid="stPageLink"] a:hover, .st-key-gc_topbar [data-testid="stPopover"] button:hover {{
          border-color: {PAL['accent']}; }}
.st-key-gc_topbar [data-testid="stPageLink"] p, .st-key-gc_topbar [data-testid="stPopover"] p {{ font-size: 0.86rem; white-space: nowrap; }}
.gc-top-brand {{ display:flex; align-items:center; gap: 0.65rem; }}
.gc-top-brand b {{ font-size: 1.12rem; font-weight: 700; color: {PAL['text']}; letter-spacing: -0.01em; }}
.gc-top-brand small {{ display:block; white-space: nowrap; font-size: 0.74rem; color: {PAL['sub']}; }}
.gc-top-brand .gc-ver {{ font-size: 0.7rem; color: {PAL['accent']}; border: 1px solid {PAL['card_border']};
          border-radius: 6px; padding: 0 0.35rem; margin-left: 0.2rem; }}
.gc-fig {{ margin: 0.6rem 0 1.2rem 0; }}
.gc-fig img {{ max-width: 100%; border: 1px solid {PAL['card_border']}; border-radius: 10px; }}
.gc-fig figcaption {{ font-size: 0.8rem; color: {PAL['sub']}; margin-top: 0.3rem; }}
.gc-doc h3 {{ font-size: 1.12rem; margin-top: 1.2rem; }}
.gc-ref {{ font-size: 0.9rem; margin: 0 0 0.55rem 0; line-height: 1.45; }}
.gc-ref b {{ color: {PAL['text']}; }}
.gc-ref span {{ color: {PAL['sub']}; font-size: 0.78rem; }}
.gc-hero {{ display:flex; gap: 1.1rem; align-items:center; margin-bottom: 0.6rem; }}
.gc-hero h2 {{ margin: 0; padding: 0; font-size: 1.6rem; font-weight: 700; color: {PAL['text']}; }}
.gc-hero p {{ margin: 0.15rem 0 0 0; color: {PAL['sub']}; }}
</style>
""", unsafe_allow_html=True)



# ================= Data =================
@st.cache_data(show_spinner=False)
def process(name, content):
    raw = data.load_file(name, content)
    clean, report = data.clean_data(raw)
    std, mapping = data.standardize(clean)
    return clean, report, std, mapping


# ---- sidebar: data source (language and theme are in the top bar) ----
LANG_SHORT = {"id": "ID", "en": "EN", "ja": "JA"}
THEME_ICON = {"System": ":material/brightness_auto:", "Light": ":material/light_mode:",
              "Dark": ":material/dark_mode:"}

uploaded = st.sidebar.file_uploader(t("Data file (CSV or Excel)"),
                                    type=["csv", "xlsx"], key="uploader")
if HOSTED:
    st.sidebar.caption(t("Online version: files are processed in memory and are not "
                         "stored. For confidential data, use the desktop or portable "
                         "version."))
if uploaded is not None:
    # load a newly chosen file once; other tools may replace the dataset later
    if st.session_state.get("_upload_id") != uploaded.file_id:
        st.session_state["dataset"] = (uploaded.name, uploaded.getvalue())
        st.session_state["_upload_id"] = uploaded.file_id
elif st.session_state.pop("_upload_id", None):
    # the file was removed with the x button in this session
    if st.session_state.get("dataset", ("",))[0] != "xrf_quantified.csv":
        st.session_state.pop("dataset", None)

ctx = None
if "dataset" in st.session_state:
    name, content = st.session_state["dataset"]
    clean, report, std, mapping = process(name, content)
    ctx = {"name": name, "clean": clean, "report": report, "std": std,
           "mapping": mapping}


# ================= Helpers =================
def header(title, sub=None):
    chip = ""
    if ctx:
        chip = (f'<span class="gc-chip"><b>{ctx["name"]}</b>&nbsp; '
                + t("{a} of {b} samples shown").format(a=len(view()), b=len(ctx["std"]))
                + "</span>")
    st.markdown(f'<div class="gc-header"><h1>{title}</h1>{chip}</div>',
                unsafe_allow_html=True)
    if sub:
        st.markdown(f'<p class="gc-sub">{sub}</p>', unsafe_allow_html=True)


def view():
    """Samples currently selected in the sidebar."""
    df = ctx["std"]
    g = st.session_state.get("group_col", NONE)
    keep = st.session_state.get("group_keep")
    if g != NONE and g in df and keep is not None:
        df = df[df[g].astype(str).fillna("(blank)").isin(keep)]
    return df


def group_names(g):
    """All group names in the whole file (not only the shown ones),
    so each group keeps the same symbol when others are hidden."""
    if g is None:
        return ["All samples"]
    return pd.unique(ctx["std"][g].astype(str).fillna("(blank)")).tolist()


def symbol_table(g):
    """Style table {group: {colour, symbol, size, filled}} for a grouping."""
    store = st.session_state.setdefault("symbols", {})
    key = g or "__all__"
    store[key] = symbols.auto_styles(group_names(g), settings["palette"],
                                     store.get(key))
    return store[key]


def opts(df, labels=True):
    """Keyword arguments shared by all plots: symbols, labels and legend."""
    g = st.session_state.get("group_col", NONE)
    g = None if g == NONE else g
    lab = st.session_state.get("label_col", NONE)
    kw = {"sty": symbols.resolve(df, g, symbol_table(g),
                                 use_file=settings["use_file_styles"]),
          "legend_title": g, "legend": settings["legend"]}
    if labels:
        kw["labels"] = df[lab] if lab != NONE and lab in df else None
    return kw


def show(fig, max_width="100%"):
    """Show a figure inline (as SVG inside the page, not as a separate file)."""
    st.markdown(plotting.figure_html(fig, max_width), unsafe_allow_html=True)


MIME = {"png": "image/png", "svg": "image/svg+xml", "pdf": "application/pdf",
        "csv": "text/csv"}


def downloads(make_fig, stem):
    """Download buttons. The file is only created when a button is clicked,
    so nothing is downloaded when the page opens."""
    style = settings["export_style"]
    style = SCREEN if style == "screen" else style
    dpi = settings["dpi"]
    app = dict(appearance)
    cols = st.columns(3)
    for col, fmt in zip(cols, ("png", "svg", "pdf")):
        def make(fmt=fmt):
            plotting.set_appearance(app)
            return plotting.figure_bytes(make_fig(style), fmt, dpi)
        col.download_button(t("Download {f}").format(f=fmt.upper()), data=make,
                            file_name=f"{stem}.{fmt}", mime=MIME[fmt],
                            on_click="ignore", width="stretch",
                            key=f"dl_{stem}_{fmt}")


def csv_download(label, make_table, file_name, index=False):
    st.download_button(label,
                       data=lambda: make_table().to_csv(index=index).encode("utf-8"),
                       file_name=file_name, mime=MIME["csv"], on_click="ignore")


def missing_note(need):
    st.info(t("This diagram needs these columns: {c}. Check the Data page to see "
              "which columns were recognised.").format(c=", ".join(need)))


def empty_state():
    st.markdown(f"""
<div class="gc-empty">
<h2>{t("Plot your rock data in a few clicks")}</h2>
<p>{t("Load a CSV or Excel file in the left panel. Put one sample per row and the column names in the first row, for example Sample, SiO2, MgO, La, Ce. Values like &lt;0.01, n.d. or bdl are handled for you.")}</p>
</div>""", unsafe_allow_html=True)
    if st.button(t("Try the example dataset"), type="primary"):
        st.session_state["dataset"] = (EXAMPLE_FILE.name, EXAMPLE_FILE.read_bytes())
        st.rerun()


def catalog_coords(d, df):
    """Coordinates for every panel of a catalogue diagram (None = missing data)."""
    out, missing = [], []
    for i in range(len(d["panels"])):
        try:
            out.append(catalog.panel_data(d, i, df, settings))
            missing.append(None)
        except calc.MissingData as e:
            out.append(None)
            missing.append(str(e.args[0]))
    return out, missing


def catalog_figure(d, df, style=None, only=None, panel_size=(4.6, 3.9), kw=None):
    coords, _ = catalog_coords(d, df)
    kw = kw or opts(df)
    return plotting.plot_catalog(d, coords, style=style or SCREEN, only=only,
                                 panel_size=panel_size, **kw)


def classification_table(d, df):
    """Field name per sample for every panel that has fields."""
    coords, _ = catalog_coords(d, df)
    cols = {}
    for i, c in enumerate(coords):
        if c is None:
            continue
        names = plotting.classify_panel(d, i, c)
        if names is not None:
            label = d["title"] if len(coords) == 1 else d["geometry"][i].get("name", f"Panel {i + 1}")
            cols[label] = names
    return pd.DataFrame(cols, index=df.index)


def card_head(title, sub, key, target=None, did=None):
    a, b = st.columns([5, 1])
    a.markdown(f'<p class="gc-card-title">{title}</p>'
               f'<p class="gc-card-sub">{sub}</p>', unsafe_allow_html=True)
    if b.button(t("Open"), key=key, width="stretch"):
        if did:
            st.session_state["diagram_id"] = did
        st.switch_page(target)


# ================= Pages =================
def page_dashboard():
    header(t("Dashboard"))
    if ctx is None:
        empty_state()
        return
    df = view()
    kw = opts(df)
    small = (5.4, 4.1)
    top = st.columns(2, gap="medium")
    for col, did, sub in ((top[0], "TAS", t("Volcanic rock names, IUGS")),
                          (top[1], "AFM", t("Tholeiitic or calc-alkaline series"))):
        with col, st.container(border=True):
            card_head(DIA[did]["title"], sub, f"open_{did}", PAGES["diagrams"], did)
            _, miss = catalog_coords(DIA[did], df)
            if miss[0]:
                missing_note([miss[0]])
            else:
                show(catalog_figure(DIA[did], df, panel_size=small, kw=kw))
    bottom = st.columns(2, gap="medium")
    with bottom[0], st.container(border=True):
        ref = REE
        norm = calc.normalize(df, REE)
        if norm.shape[1] < 3:
            ref, norm = MULTI, calc.normalize(df, MULTI)
        card_head(t("Spider diagram"), ref["title"], "open_spider", PAGES["spider"])
        if norm.shape[1] < 3:
            missing_note([t("trace elements in ppm, e.g. La, Ce, Nd ... Lu")])
        else:
            show(plotting.plot_spider(norm, ref, style=SCREEN, size=small,
                                      **opts(df, labels=False)))
    with bottom[1], st.container(border=True):
        card_head(t("Samples"), t("Location and rock names"), "open_data", PAGES["data"])
        if "Latitude" in df and "Longitude" in df and \
                df[["Latitude", "Longitude"]].notna().any().all():
            st.map(df.rename(columns={"Latitude": "lat", "Longitude": "lon"})
                   .dropna(subset=["lat", "lon"]), height=200, size=200,
                   color="#4FB39A")
        else:
            st.caption(t("Add Latitude and Longitude columns (decimal degrees) to "
                         "see sample locations on a map."))
        g = kw["legend_title"]
        id_col = df.columns[0]
        cols = [id_col] + [c for c in (g, "SiO2", "MgO") if c and c in df and c != id_col]
        table = df[cols].copy()
        for did in ("TAS", "AFM"):
            ct = classification_table(DIA[did], df)
            if not ct.empty:
                table[did] = ct.iloc[:, 0]
        st.dataframe(table, hide_index=True, height=250)


def diagram_status(d, df):
    _, miss = catalog_coords(d, df)
    ok = sum(m is None for m in miss)
    return ok, len(miss), [m for m in miss if m]


def page_diagrams():
    header(t("Diagrams"), t("Classification and discrimination diagrams. Boundaries "
                            "are taken from GCDkit 6.3, so results match GCDkit."))
    if ctx is None:
        empty_state()
        return
    df = view()
    left, right = st.columns([1.1, 3], gap="large")
    with left:
        q = st.text_input(t("Search"), placeholder=t("Search name, author or rock type"),
                          label_visibility="collapsed", key="dia_search")
        only_ready = st.toggle(t("Only diagrams my data can fill"), key="dia_ready")
        ids = []
        with st.container(height=640, border=False):
            for cat in catalog.CATEGORIES:
                rows = []
                for d in catalog.DIAGRAMS:
                    if d["category"] != cat:
                        continue
                    text = " ".join([d["title"], d["scope"], cat, t(cat), d["reference"]]).lower()
                    if q and q.lower() not in text:
                        continue
                    ok, n, _ = diagram_status(d, df)
                    if only_ready and ok == 0:
                        continue
                    rows.append((d, ok, n))
                if not rows:
                    continue
                st.markdown(f'<p class="gc-nav-head" style="margin-left:0">{t(cat)}</p>',
                            unsafe_allow_html=True)
                cur = st.session_state.get("diagram_id", "TAS")
                for d, ok, n in rows:
                    ids.append(d["id"])
                    icon = (":material/check_circle:" if ok == n else
                            ":material/error:" if ok else ":material/block:")
                    if st.button(d["title"], key=f"dia_{d['id']}", icon=icon,
                                 type="primary" if d["id"] == cur else "tertiary",
                                 width="stretch"):
                        st.session_state["diagram_id"] = d["id"]
                        st.rerun()
        if not ids:
            st.info(t("No diagram matches. Clear the search or the filter."))
            return
        st.caption(t("Tick: your data fill every panel. Warning: some panels lack "
                     "data. Crossed circle: needed columns are missing."))
        did = st.session_state.get("diagram_id", "TAS")
        if did not in ids:
            did = ids[0]
            st.session_state["diagram_id"] = did
    d = DIA[did]
    ok, n, miss = diagram_status(d, df)
    with right:
        st.markdown(f'<p class="gc-card-title" style="font-size:1.15rem">{d["title"]}</p>'
                    f'<p class="gc-meta"><span class="gc-tag">{t(d["category"])}</span>'
                    f'<span class="gc-tag">{d["scope"]}</span>'
                    f'<span class="gc-tag">{d["year"]}</span>'
                    + ('<span class="gc-tag ok">IUGS</span>' if d.get("iugs") else "")
                    + (f'<span class="gc-tag ok">' + t("{a} of {b} panels ready").format(a=ok, b=n)
                       + "</span>" if n > 1 else "")
                    + "</p>", unsafe_allow_html=True)
        if ok == 0:
            missing_note(sorted(set(miss)))
        else:
            kw = opts(df)
            size = (6.2, 4.9) if n == 1 else (4.4, 3.8)
            show(catalog_figure(d, df, panel_size=size, kw=kw),
                 max_width="780px" if n == 1 else "100%")
            if miss:
                st.caption(t("Panels without data: missing {c}.").format(
                    c=", ".join(sorted(set(miss)))))
            downloads(lambda s_: catalog_figure(d, df, style=s_, kw=kw,
                                                panel_size=size), d["id"])
        t1, t2 = st.tabs([t("Results"), t("Scientific basis")])
        with t1:
            ct = classification_table(d, df) if ok else pd.DataFrame()
            if ct.empty:
                st.caption(t("This diagram has no named fields to assign samples to; "
                             "read the position of each sample on the plot."))
            else:
                res = pd.concat([df.iloc[:, [0]], ct], axis=1)
                if ct.shape[1] == 1:
                    st.dataframe(ct.iloc[:, 0].value_counts().rename_axis(t("Field"))
                                 .reset_index(name=t("Samples")), hide_index=True)
                st.dataframe(res, hide_index=True, height=260)
                csv_download(t("Download results (CSV)"), lambda: res,
                             f"{d['id']}_results.csv")
        with t2:
            rows = []
            for i, p in enumerate(d["panels"]):
                if p["kind"] == "binary":
                    rows.append(f"- **{t('Panel')} {i + 1}:** x = {p['xlab']}, y = {p['ylab']}"
                                + (f" ({t('anhydrous, 100 wt%')})" if p.get("basis") == "anhydrous"
                                   and settings["tas_recalc"] else ""))
                else:
                    a_, b_, c_ = p["apices"]
                    rows.append(f"- **{t('Panel')} {i + 1}:** "
                                + t("ternary, apices {a} (left), {b} (top), {c} (right)")
                                .format(a=a_, b=b_, c=c_))
            st.markdown("\n".join(rows))
            if d.get("notes"):
                st.markdown(d["notes"])
            st.markdown(f"**{t('Reference')}:** {d['reference']}\n\n"
                        f"**{t('Boundaries')}:** {d['source']} (Janousek et al. 2006, GPL).")


def page_data():
    header(t("Data"))
    if ctx is None:
        empty_state()
        return
    df = view()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(t("Samples"), len(df))
    c2.metric(t("Columns"), df.shape[1])
    c3.metric(t("Recognised columns"), len(ctx["mapping"]))
    c4.metric(t("Cells set to missing"),
              int(ctx["report"]["Cells set to missing"].sum())
              if not ctx["report"].empty else 0)

    tab1, tab2, tab3, tab4 = st.tabs([t("Table"), t("Data check"),
                                      t("Calculated values"), t("CIPW norm")])
    with tab1:
        st.dataframe(df, hide_index=True)
    with tab2:
        if ctx["report"].empty:
            st.success(t("All numeric columns were read without problems."))
        else:
            st.warning(t("Some cells could not be read as numbers and were set to "
                         "missing. Check that this is what you expect."))
            st.dataframe(ctx["report"], hide_index=True)
        if settings["xrf_qc"]:
            um = ultramafic_rows(df)
            if um is not None and not um.empty:
                st.warning(t("{n} ultramafic samples (MgO >= {m} wt%). If T-Fe2O3 was "
                             "measured by XRF without a Ca-Mg matrix correction, it may be "
                             "~0.6-0.7 wt% too high and Mg# too low (Mikuni et al. 2025).")
                           .format(n=len(um), m=settings["um_mgo"]),
                           icon=":material/science:")
                st.page_link(PAGES["xrfqc"], label=t("Open the ultramafic check"),
                             icon=":material/fact_check:")
        st.markdown(f"**{t('Recognised columns')}**")
        st.dataframe(pd.DataFrame({t("In your file"): list(ctx["mapping"].values()),
                                   t("Read as"): list(ctx["mapping"].keys())}),
                     hide_index=True)
    with tab3:
        derived = calc.derived_table(df, settings["tas_recalc"])
        for did, label in (("TAS", "TAS"), ("AFM", "AFM")):
            ct = classification_table(DIA[did], df)
            if not ct.empty:
                derived[label] = ct.iloc[:, 0]
        out = pd.concat([df.iloc[:, [0]], derived], axis=1)
        st.dataframe(out.round(3), hide_index=True)
        st.caption(t("FeOt = FeO + 0.8998 x Fe2O3. Mg# = 100 x Mg / (Mg + Fe2+), "
                     "molar, with all iron as Fe2+."))
        csv_download(t("Download data with calculated values (CSV)"),
                     lambda: pd.concat([df, derived], axis=1), "geochem_calculated.csv")
    with tab4:
        if "SiO2" not in df:
            missing_note(["SiO2", "Al2O3", "..."])
        else:
            recast = st.toggle(t("Recast the norm to 100 %"), value=False)
            table, n_split = norms.cipw(df, settings["fe3_ratio"], normsum=recast)
            res = pd.concat([df.iloc[:, [0]], norms.compact(table).round(2)], axis=1)
            st.dataframe(res, hide_index=True)
            if n_split:
                st.caption(t("Iron was split into FeO and Fe2O3 for {n} samples with "
                             "Fe3+/Fe(total) = {r} (change in Settings).")
                           .format(n=n_split, r=settings["fe3_ratio"]))
            st.caption(t("CIPW norm after Hutchison (1974, 1975), ported from GCDkit. "
                         "Values in wt%."))
            csv_download(t("Download CIPW norm (CSV)"), lambda: res, "cipw_norm.csv")


def page_spider():
    header(t("Spider diagrams"))
    if ctx is None:
        empty_state()
        return
    df = view()
    kw = opts(df, labels=False)
    choice_ = st.radio(t("Pattern"), [REE["title"], MULTI["title"]], horizontal=True)
    ref = REE if choice_ == REE["title"] else MULTI
    norm = calc.normalize(df, ref)
    if norm.shape[1] < 3:
        missing_note(list(ref["elements"].keys()))
        return
    missing = [e for e in ref["elements"] if e not in norm.columns]
    left, right = st.columns([3, 2], gap="large")
    with left:
        show(plotting.plot_spider(norm, ref, style=SCREEN, **kw))
        downloads(lambda s: plotting.plot_spider(norm, ref, style=s, **kw),
                  "spider_" + ref["id"])
    with right:
        st.markdown(f"**{t('Normalized values')}**")
        st.dataframe(pd.concat([df.iloc[:, [0]], norm.round(3)], axis=1),
                     hide_index=True, height=260)
        if missing:
            st.caption(t("Not in your data, so not plotted: {c}").format(c=", ".join(missing)))
        with st.expander(t("Scientific basis")):
            st.markdown(f"- {t('Normalizing values')}: {ref['reference']}\n"
                        f"- {t('K, Ti and P are calculated from K2O, TiO2 and P2O5 when the element columns are missing.')}\n"
                        f"- {t('Values below detection limit are left out; dotted lines bridge the gaps.')}")


def page_xy():
    header(t("XY plot"))
    if ctx is None:
        empty_state()
        return
    df = view()
    kw = opts(df)
    num = df.select_dtypes(include="number").columns.tolist()
    if len(num) < 2:
        st.warning(t("At least two numeric columns are needed."))
        return
    left, right = st.columns([1, 3], gap="large")
    with left:
        x = st.selectbox(t("X axis"), num, index=0)
        y = st.selectbox(t("Y axis"), num, index=1)
        lx = st.checkbox(t("Log scale X"))
        ly = st.checkbox(t("Log scale Y"))
    with right:
        show(plotting.plot_binary(df, x, y, log_x=lx, log_y=ly, style=SCREEN, **kw),
             max_width="820px")
        downloads(lambda s: plotting.plot_binary(df, x, y, log_x=lx, log_y=ly,
                                                 style=s, **kw), f"{x}_vs_{y}")


def page_stats():
    header(t("Statistics"))
    if ctx is None:
        empty_state()
        return
    df = view()
    g = st.session_state.get("group_col", NONE)
    g = None if g == NONE else g
    num = df.select_dtypes(include="number").columns.tolist()
    default = [c for c in ("SiO2", "MgO", "FeOt", "Na2O", "K2O") if c in num] or num[:5]
    cols = st.multiselect(t("Columns"), num, default=default)
    if not cols:
        return
    stats = df.groupby(g)[cols].describe().T if g else df[cols].describe().T
    st.dataframe(stats.round(3))
    csv_download(t("Download statistics (CSV)"), lambda: stats, "statistics.csv",
                 index=True)


LEGEND_PLACES = ["upper right", "upper left", "lower right", "lower left",
                 "outside", "hidden"]
LEGEND_LABELS = {"upper right": "Top right", "upper left": "Top left",
                 "lower right": "Bottom right", "lower left": "Bottom left",
                 "outside": "Outside the plot (right)", "hidden": "Hidden"}


def _reset_symbol_widgets():
    """New widget keys so the editors show the new values."""
    st.session_state["sym_ver"] = st.session_state.get("sym_ver", 0) + 1


def preview_figure(df, kw):
    if not catalog_coords(DIA["TAS"], df)[1][0]:
        return catalog_figure(DIA["TAS"], df, panel_size=(5.0, 4.1), kw=kw)
    num = df.select_dtypes(include="number").columns.tolist()
    if len(num) >= 2:
        return plotting.plot_binary(df, num[0], num[1], style=SCREEN,
                                    size=(5.0, 4.0), **kw)
    return None


def page_symbols():
    header(t("Symbols and colours"))
    if ctx is None:
        empty_state()
        return
    g = st.session_state.get("group_col", NONE)
    g = None if g == NONE else g
    table = symbol_table(g)
    ver = st.session_state.get("sym_ver", 0)
    gkey = g or "__all__"
    if g is None:
        st.info(t("No grouping is selected, so all samples share one style. Choose "
                  "\"Group samples by\" in the left panel to give each group its own "
                  "symbol and colour."))
    else:
        st.caption(t("One row per group of \"{g}\". The styles are used in every "
                     "diagram and in exported figures.").format(g=g))
    left, right = st.columns([3, 2], gap="large")
    with left:
        top = st.columns([2, 2, 2])
        pal = top[0].selectbox(t("Colour set"), list(symbols.PALETTES), format_func=t,
                               index=list(symbols.PALETTES).index(settings["palette"]))
        if top[1].button(t("Apply colour set to all groups"), width="stretch"):
            settings["palette"] = pal
            cols = symbols.PALETTES[pal]
            for i, nm in enumerate(table):
                table[nm]["colour"] = cols[i % len(cols)]
            _reset_symbol_widgets()
            st.rerun()
        if top[2].button(t("Reset symbols"), width="stretch"):
            st.session_state["symbols"].pop(gkey, None)
            settings["palette"] = pal
            _reset_symbol_widgets()
            st.rerun()
        head = st.columns([3, 1.3, 3, 3, 1.4])
        for c, txt in zip(head, [t("Group"), t("Colour"), t("Symbol"), t("Size"),
                                 t("Filled")]):
            c.markdown(f"**{txt}**")
        for i, (nm, sty) in enumerate(table.items()):
            row = st.columns([3, 1.3, 3, 3, 1.4], vertical_alignment="center")
            row[0].write(nm)
            k = f"sym_{ver}_{gkey}_{i}"
            sty["colour"] = row[1].color_picker(
                t("Colour"), to_hex(sty["colour"]), key=k + "_c",
                label_visibility="collapsed")
            sty["symbol"] = row[2].selectbox(
                t("Symbol"), symbols.MARKER_NAMES, format_func=t,
                index=symbols.MARKER_NAMES.index(sty["symbol"]),
                key=k + "_m", label_visibility="collapsed")
            sty["size"] = row[3].slider(t("Size"), 3, 16, int(sty["size"]),
                                        key=k + "_s", label_visibility="collapsed")
            sty["filled"] = row[4].checkbox(
                t("Filled"), sty["filled"], key=k + "_f", label_visibility="collapsed",
                disabled=symbols.MARKERS[sty["symbol"]] in symbols.LINE_MARKERS)
        st.divider()
        o1, o2 = st.columns(2)
        settings["legend"] = o1.selectbox(
            t("Legend position"), LEGEND_PLACES,
            format_func=lambda v: t(LEGEND_LABELS[v]),
            index=LEGEND_PLACES.index(settings["legend"]))
        fc = {k: v for k, v in symbols.file_columns(ctx["std"]).items() if v}
        if fc:
            settings["use_file_styles"] = o2.toggle(
                t("Use the style columns in my data file"), settings["use_file_styles"],
                help=t("Found: {c}. Per-sample values override the group style "
                       "(GCDkit convention).").format(c=", ".join(fc.values())))
        else:
            o2.caption(t("Tip: a data file can carry its own Symbol, Colour and Size "
                         "columns, as in GCDkit. They are picked up automatically."))
        st.divider()
        s1, s2 = st.columns(2)
        with s1:
            csv_download(t("Save this symbol set (CSV)"),
                         lambda: pd.DataFrame(table).T.rename_axis("Group").reset_index(),
                         f"symbols_{gkey}.csv")
        with s2:
            up = st.file_uploader(t("Load a saved symbol set"), type=["csv"],
                                  key=f"symload_{ver}", label_visibility="collapsed")
            if up is not None:
                saved = pd.read_csv(up).set_index("Group")
                for nm in table:
                    if nm in saved.index:
                        r = saved.loc[nm]
                        table[nm] = {"colour": str(r["colour"]), "symbol": str(r["symbol"]),
                                     "size": int(r["size"]), "filled": bool(r["filled"])}
                _reset_symbol_widgets()
                st.rerun()
    with right:
        st.markdown(f"**{t('Preview')}**")
        df = view()
        fig = preview_figure(df, opts(df))
        if fig is not None:
            show(fig)


def page_appearance():
    header(t("Plot appearance"), t("Fonts, label orientation and lines for every "
                                   "diagram and graph, on screen and in exported files."))
    a = appearance
    ver = st.session_state.get("app_ver", 0)
    left, right = st.columns([2, 3], gap="large")
    with left:
        with st.container(border=True):
            st.markdown(f"**{t('Text')}**")
            a["font_family"] = st.radio(t("Font"), ["sans-serif", "serif"],
                                        format_func=lambda v: t("Sans-serif") if v == "sans-serif" else t("Serif (journal style)"),
                                        index=["sans-serif", "serif"].index(a["font_family"]),
                                        horizontal=True, key=f"ap_ff_{ver}")
            a["font_axis"] = st.slider(t("Axis titles (pt)"), 6.0, 16.0, float(a["font_axis"]), 0.5, key=f"ap_fa_{ver}")
            a["font_tick"] = st.slider(t("Tick labels (pt)"), 5.0, 14.0, float(a["font_tick"]), 0.5, key=f"ap_ft_{ver}")
            a["font_field"] = st.slider(t("Field names in diagrams (scale)"), 0.5, 2.0, float(a["font_field"]), 0.05, key=f"ap_fd_{ver}")
            a["font_legend"] = st.slider(t("Legend (pt)"), 5.0, 14.0, float(a["font_legend"]), 0.5, key=f"ap_fl_{ver}")
            a["font_point"] = st.slider(t("Sample labels (pt)"), 4.0, 12.0, float(a["font_point"]), 0.5, key=f"ap_fp_{ver}")
        with st.container(border=True):
            st.markdown(f"**{t('Label orientation')}**")
            modes = ["template", "horizontal", "hidden"]
            mode_lab = {"template": "As in GCDkit (rotated along boundaries)",
                        "horizontal": "All horizontal", "hidden": "Hidden"}
            a["field_labels"] = st.radio(t("Field names"), modes,
                                         format_func=lambda v: t(mode_lab[v]),
                                         index=modes.index(a["field_labels"]), key=f"ap_fm_{ver}")
            a["tick_rotation_x"] = st.select_slider(t("X tick labels (degrees)"),
                                                    [0, 30, 45, 60, 90],
                                                    value=int(a["tick_rotation_x"]), key=f"ap_tr_{ver}")
            a["ylabel_rotation"] = st.radio(t("Y axis title"), ["vertical", "horizontal"],
                                            format_func=lambda v: t("Vertical") if v == "vertical" else t("Horizontal"),
                                            index=["vertical", "horizontal"].index(a["ylabel_rotation"]),
                                            horizontal=True, key=f"ap_yr_{ver}")
        with st.container(border=True):
            st.markdown(f"**{t('Lines and size')}**")
            a["line_width"] = st.slider(t("Boundary line width"), 0.3, 3.0, float(a["line_width"]), 0.1, key=f"ap_lw_{ver}")
            a["marker_edge"] = st.slider(t("Symbol outline width"), 0.0, 2.0, float(a["marker_edge"]), 0.1, key=f"ap_me_{ver}")
            a["size_scale"] = st.slider(t("Figure size (scale)"), 0.6, 1.6, float(a["size_scale"]), 0.05, key=f"ap_ss_{ver}")
            a["grid"] = st.toggle(t("Grid in classification diagrams"), bool(a["grid"]), key=f"ap_gr_{ver}")
            a["panel_titles"] = st.toggle(t("Panel titles in multi-panel diagrams"), bool(a["panel_titles"]), key=f"ap_pt_{ver}")
        if st.button(t("Reset to defaults"), icon=":material/restart_alt:"):
            st.session_state["appearance"] = dict(plotting.APPEARANCE_DEFAULT)
            st.session_state["app_ver"] = ver + 1
            st.rerun()
    plotting.set_appearance(a)
    with right:
        st.markdown(f"**{t('Preview')}**")
        if ctx is None:
            st.caption(t("Load data to see a preview."))
        else:
            df = view()
            fig = preview_figure(df, opts(df))
            if fig is not None:
                show(fig, max_width="760px")


def page_settings():
    header(t("Settings"))
    with st.container(border=True):
        st.markdown(f"**{t('Calculations')}**")
        settings["tas_recalc"] = st.toggle(
            t("Recalculate major oxides to 100 % volatile-free before TAS"),
            value=settings["tas_recalc"], help=t("Recommended by Le Bas et al. (1986)."))
        settings["fe3_ratio"] = st.slider(
            t("Fe3+/Fe(total) used when only total iron is measured (CIPW norm, Verma 2006)"),
            0.0, 0.5, float(settings["fe3_ratio"]), 0.01)
    with st.container(border=True):
        st.markdown(f"**{t('Optional modules')}**")
        st.caption(t("Turn on only what fits your samples. A module adds its own page "
                     "under Tools."))
        on = st.toggle(t("XRF quality control (Mikuni et al. 2025)"),
                       value=settings["xrf_qc"],
                       help=t("Reference-material QC plots, accuracy (Eq. 7), a library of "
                              "26 reference materials and an iron check for ultramafic "
                              "rocks. Useful for peridotite and serpentinite samples."))
        if on != settings["xrf_qc"]:
            settings["xrf_qc"] = on
            st.rerun()
        if on:
            settings["um_mgo"] = st.slider(
                t("Ultramafic check: MgO at or above (wt%)"), 15.0, 45.0,
                float(settings["um_mgo"]), 1.0)
    with st.container(border=True):
        st.markdown(f"**{t('Figure export')}**")
        labels = {"publication": t("Publication (white background, no field colours)"),
                  "screen": t("Same as screen")}
        settings["export_style"] = st.radio(
            t("Style"), list(labels), format_func=labels.get,
            index=list(labels).index(settings["export_style"]))
        settings["dpi"] = st.select_slider(t("Resolution (dpi)"), [150, 300, 600],
                                           value=settings["dpi"])
    st.page_link(PAGES["about"], label=t("About GeoChem App, license and how to cite"),
                 icon=":material/info:")


def sample_names(df):
    lab = st.session_state.get("label_col", NONE)
    col = lab if lab != NONE and lab in df else df.columns[0]
    return data._as_text(df[col])


@st.cache_data(show_spinner=False)
def _rm_detect(df):
    return xrfqc.detect(df, RM_LIB)


def ultramafic_rows(df):
    """Ultramafic samples (reference materials themselves are left out)."""
    rm = _rm_detect(ctx["std"]).reindex(df.index)
    smp = df[rm.isna()]
    return xrfqc.ultramafic_check(smp, sample_names(smp), settings["um_mgo"])


RM_LIB = xrfqc.load_library()


@st.cache_data(show_spinner=False)
def _read_intensities(name, content):
    raw = data.load_file(name, content)
    clean, _ = data.clean_data(raw)
    return clean


def xrf_calibration_tab():
    """Calibration lines from raw X-ray intensities (Mikuni et al. 2025)."""
    st.caption(t("Upload the raw X-ray intensities of your glass beads: one row per bead "
                 "with the sample name, the dilution factor (DF), LOI (wt%) and one "
                 "intensity column per element (Si, Ti, Al, Fe, Mn, Mg, Ca, Na, K, P, Cr, "
                 "Ni; names like \"Si Ka\" or \"SiO2\" also work). Rows named like a "
                 "reference material (JP-1, JB-1a ...) are used as calibration standards; "
                 "all other rows are quantified."))
    c1, c2 = st.columns([3, 1], vertical_alignment="bottom")
    up = c1.file_uploader(t("Intensity file (CSV or Excel)"), type=["csv", "xlsx", "xls"],
                          key="xrf_int_up")
    if up is not None and st.session_state.get("_xrf_up_id") != up.file_id:
        st.session_state["xrf_int"] = (up.name, up.getvalue())
        st.session_state["_xrf_up_id"] = up.file_id
    if c2.button(t("Load the example from the paper"), width="stretch",
                 help=t("Data set SciTokyo_Day1 (Mikuni et al. 2025, Tables 1 and 3).")):
        st.session_state["xrf_int"] = (xrfcal.EXAMPLE_FILE.name,
                                       xrfcal.EXAMPLE_FILE.read_bytes())
    if "xrf_int" not in st.session_state:
        return
    name, content = st.session_state["xrf_int"]
    try:
        tab = _read_intensities(name, content)
    except Exception as e:          # unreadable file
        st.error(t("The file could not be read: {e}").format(e=e))
        return
    cols, df_col, loi_col = xrfcal.find_columns(tab)
    text = tab.select_dtypes(exclude="number").columns
    if len(text) == 0:
        st.error(t("No sample-name column was found."))
        return
    names = data._as_text(tab[text[0]])
    st.markdown(f'<p class="gc-meta"><b>{name}</b> &middot; '
                + t("{n} beads, {k} elements recognised").format(n=len(tab), k=len(cols))
                + f": {', '.join(xrfcal.label(o) for o in cols)}</p>",
                unsafe_allow_html=True)
    if df_col is None:
        st.error(t("A dilution-factor column (DF) is needed: (sample + flux) / sample "
                   "for each bead."))
        return
    if loi_col is None:
        st.warning(t("No LOI column: standards use the LOI of Mikuni et al. (2025) and "
                     "unknowns are reported on the ignited (LOI-free) basis."))
    auto = xrfcal.standards(names, RM_LIB)
    choices = [i for i in auto.dropna().index]
    fmt = lambda i: f"{names[i]}"
    with st.container(border=True):
        a, b = st.columns([3, 2], gap="large")
        keep = a.multiselect(t("Calibration standards"), choices, default=choices,
                             format_func=fmt, key=f"xrf_std_{name}")
        a.caption(t("Matched by name to the reference library. Remove a standard to see "
                    "its effect (for example, keep only JP-1 and JP-2 as ultramafic RMs)."))
        corr_on = b.toggle(t("Matrix correction for T-Fe2O3"), value=True, key="xrf_corr_on")
        corr_el = b.multiselect(t("Correcting elements"),
                                [o for o in xrfcal.OXIDES if o not in ("Fe2O3t",) and o in cols],
                                default=[o for o in ("CaO", "MgO") if o in cols],
                                format_func=xrfcal.label, key="xrf_corr_el",
                                disabled=not corr_on)
        b.caption(t("Ca and Mg are recommended (Mikuni et al. 2025). Factors larger than "
                    "0.1 are marked as doubtful."))
    std = auto.where(auto.index.isin(keep), pd.NA)
    if std.notna().sum() < 3:
        st.info(t("At least three calibration standards are needed."))
        return
    corrections = {"Fe2O3t": corr_el} if corr_on and corr_el else {}
    cal = xrfcal.calibrate(tab, cols, df_col, loi_col, std, RM_LIB, corrections)
    out, fe_plain, complete = xrfcal.quantify(tab, cal, names)
    summ = cal["summary"]
    fe = cal["lines"].get("Fe2O3t")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(t("Standards"), int(std.notna().sum()))
    m2.metric(t("Unknowns quantified"), int(std.isna().sum()))
    if fe is not None:
        m3.metric(t("T-Fe2O3 accuracy (wt%)"), f"{fe['accuracy']:.3f}",
                  delta=(f"{fe['accuracy'] - cal['plain']['Fe2O3t']['accuracy']:+.3f}"
                         if fe["A"] else None), delta_color="inverse")
        m4.metric("T-Fe2O3 R²", f"{fe['r2']:.5f}")
    if fe is not None and any(abs(v) > xrfcal.MAX_FACTOR for v in fe["A"].values()):
        st.warning(t("A correction factor is larger than 0.1. Mikuni et al. (2025) do not "
                     "use such factors; try other correcting elements."))
    v1, v2, v3 = st.tabs([t("Calibration lines"), t("T-Fe2O3 deviation"), t("Results")])
    with v1:
        show(xrfcal.plot_lines(cal, tab, SCREEN))
        downloads(lambda s_: xrfcal.plot_lines(cal, tab, s_), "xrf_calibration_lines")
        st.caption(t("Orange diamonds: ultramafic standards (JP-1, JP-2, UB-N, OKUM). For "
                     "T-Fe2O3, open circles are the uncorrected intensities and the dashed "
                     "line is the uncorrected calibration."))
        st.dataframe(summ.round(5), hide_index=True)
        st.caption(t("Line: C(bead) = a x I + b (Eq. 1; Eq. 5 after correction). Accuracy: "
                     "Eq. 7 on the as-received basis, in wt%."))
        csv_download(t("Download calibration summary (CSV)"), lambda: summ,
                     "xrf_calibration_summary.csv")
    with v2:
        if fe is None:
            missing_note(["Fe"])
        else:
            show(xrfcal.plot_fe_deviation(cal, SCREEN), max_width="1000px")
            downloads(lambda s_: xrfcal.plot_fe_deviation(cal, s_), "xrf_fe_deviation")
            st.caption(t("Compare with Fig. 4b of Mikuni et al. (2025): without correction "
                         "the peridotite standards plot ~0.6-0.7 wt% too high."))
    with v3:
        res = out.copy()
        res.insert(1, t("Role"), [t("Standard") if pd.notna(std[i]) else t("Unknown")
                                  for i in res.index])
        if fe_plain is not None:
            res["T-Fe2O3 without correction"] = fe_plain
        res = res.rename(columns={"Fe2O3t": "T-Fe2O3"})
        only_unknown = st.toggle(t("Show unknowns only"), value=True, key="xrf_only_unk")
        shown = res[std.isna()] if only_unknown else res
        st.dataframe(shown.round(4), hide_index=True)
        notes = [t("Oxides in wt% on the as-received (before ignition) basis; Cr and Ni in "
                   "ug/g. Mg# = 100 Mg / (Mg + Fe), molar, all iron as Fe2+.")]
        if not complete:
            notes.append(t("Fewer than 10 oxides were measured, so the dry total was taken "
                           "as 100 wt% for the LOI conversion."))
        st.caption(" ".join(notes))
        r1, r2 = st.columns(2)
        with r1:
            csv_download(t("Download results (CSV)"),
                         lambda: res.drop(columns=[t("Role")]), "xrf_quantified.csv")
        with r2:
            if st.button(t("Use the unknowns as my dataset"), icon=":material/input:",
                         help=t("Opens the quantified samples in all diagrams.")):
                ds = res[std.isna()].drop(columns=[t("Role")])
                st.session_state["dataset"] = ("xrf_quantified.csv",
                                               ds.to_csv(index=False).encode("utf-8"))
                st.session_state.pop("group_keep", None)
                st.rerun()
    if name == xrfcal.EXAMPLE_FILE.name:
        st.caption(f"{t('Source')}: {xrfqc.CITATION}, Tables 1 and 3 (CC BY 4.0).")


def page_xrfqc():
    header(t("XRF quality control"),
           t("Based on Mikuni, Ishikawa and Sato (2025), Geochemical Journal 59, "
             "299-314. Reference values are on the as-received (before ignition) basis."))
    tab1, tab_cal, tab2, tab3 = st.tabs([t("Reference materials in my data"),
                                         t("Calibration from intensities"),
                                         t("Ultramafic check"), t("Reference library")])
    with tab_cal:
        xrf_calibration_tab()
    with tab3:
        lib = RM_LIB.reset_index()
        st.dataframe(lib, hide_index=True)
        st.caption(t("Oxides in wt%, Cr and Ni in ug/g. Fe2O3t = total iron as Fe2O3. "
                     "LOI: measured by Mikuni et al. (2025); used only when your file "
                     "has no LOI for a standard."))
        st.markdown(f"{t('Source')}: {xrfqc.CITATION}, Table 1 (CC BY 4.0). "
                    f"[{xrfqc.DOI_URL}]({xrfqc.DOI_URL})")
        csv_download(t("Download the library (CSV)"), lambda: lib,
                     "reference_materials_Mikuni2025.csv")
    if ctx is None:
        with tab1:
            empty_state()
        with tab2:
            st.caption(t("Load data to see a preview."))
        return
    full = ctx["std"]
    names = sample_names(full)
    with tab1:
        found = _rm_detect(full)
        st.caption(t("Rows are matched to a reference material by name (for example "
                     "JB-1a, JB1a or \"JP-1 run2\"). Correct or add matches in the table "
                     "below."))
        ver = st.session_state.get("rm_ver", 0)
        edit_key = f"rm_edit_{ver}_{ctx['name']}"
        base = pd.DataFrame({t("Sample"): names, "RM": found.astype(object)
                             .where(found.notna(), None)})
        with st.expander(t("Match samples to reference materials ({n} found)")
                         .format(n=int(found.notna().sum())), expanded=found.isna().all()):
            ed = st.data_editor(base, hide_index=True, disabled=[t("Sample")],
                                key=edit_key, height=260,
                                column_config={"RM": st.column_config.SelectboxColumn(
                                    "RM", options=list(RM_LIB.index))})
        rm = pd.Series(ed["RM"].values, index=full.index)
        rm = rm.where(rm.notna() & (rm.astype(str) != ""), pd.NA)
        if rm.isna().all():
            st.info(t("No reference materials found. Put the RM name (for example "
                      "JP-1 or JB-1a) in the sample column of your file, or choose it "
                      "in the table above."))
        else:
            settings["qc_tol"] = st.slider(t("Tolerance (% of the reference value)"),
                                           1.0, 20.0, float(settings["qc_tol"]), 0.5)
            tol = settings["qc_tol"]
            table = xrfqc.qc_table(full, rm, RM_LIB, names, tol)
            if table.empty:
                missing_note(xrfqc.COMPONENTS)
            else:
                n_bad = int((table["Status"] == "outside").sum())
                c1, c2, c3 = st.columns(3)
                c1.metric(t("Reference materials"), int(rm.notna().sum()))
                c2.metric(t("Values compared"), len(table))
                c3.metric(t("Outside tolerance"), n_bad)
                v1, v2 = st.tabs([t("Deviation (%)"), t("Measured vs reference")])
                with v1:
                    show(xrfqc.plot_deviation(table, SCREEN, tol), max_width="1000px")
                    downloads(lambda s_: xrfqc.plot_deviation(table, s_, tol),
                              "xrf_qc_deviation")
                with v2:
                    show(xrfqc.plot_qc(table, SCREEN, tol))
                    downloads(lambda s_: xrfqc.plot_qc(table, s_, tol), "xrf_qc_1to1")
                st.caption(t("Line: 1:1. Band: tolerance (at least 0.02 wt% or 5 ug/g). "
                             "Red ring: outside tolerance."))
                st.markdown(f"**{t('Accuracy per component')}**")
                acc = xrfqc.accuracy(table)
                st.dataframe(acc.round(4), hide_index=True)
                st.caption(t("Accuracy = sqrt(sum(C_measured - C_reference)^2 / (n - 1)), "
                             "Mikuni et al. (2025) Eq. 7. Needs at least two measurements."))
                st.markdown(f"**{t('All comparisons')}**")
                shown = table.drop(columns="key")
                st.dataframe(shown.round(4), hide_index=True)
                q1, q2 = st.columns(2)
                with q1:
                    csv_download(t("Download comparisons (CSV)"), lambda: shown,
                                 "xrf_qc_comparisons.csv")
                with q2:
                    csv_download(t("Download accuracy (CSV)"), lambda: acc,
                                 "xrf_qc_accuracy.csv")
        st.caption(t("Compare like with like: if your lab reports values on an "
                     "ignited (LOI-free) basis, recalculate them before comparing."))
    with tab2:
        settings["um_mgo"] = st.number_input(t("Ultramafic check: MgO at or above (wt%)"),
                                             15.0, 45.0, float(settings["um_mgo"]), 1.0)
        um = ultramafic_rows(full)
        if um is None:
            missing_note(["MgO", "Fe2O3t / FeOt"])
        elif um.empty:
            st.success(t("No sample has MgO at or above {m} wt%.").format(m=settings["um_mgo"]))
        else:
            st.markdown(t(
                "In peridotites, XRF gives too much X-ray intensity for iron compared with "
                "other igneous rocks (a **matrix effect**: the rest of the rock changes how "
                "strongly iron is seen). Without a Ca-Mg matrix correction, T-Fe2O3 in the "
                "peridotite reference materials JP-1, JP-2 and UB-N was **0.64-0.74 wt% too "
                "high**; with the correction the error fell to 0.03-0.13 wt%. Other major "
                "oxides and NiO showed little matrix effect."))
            st.dataframe(um.round(3), hide_index=True)
            st.caption(t("This is a sensitivity check, not a correction: it shows how much "
                         "Mg# could change. Ask your lab whether a Ca-Mg matrix correction "
                         "was applied to T-Fe2O3, and check with peridotite reference "
                         "materials (JP-1, JP-2, UB-N) in the same run."))
            csv_download(t("Download the ultramafic check (CSV)"), lambda: um,
                         "ultramafic_check.csv")


def page_docs():
    header(t("Documentation"), t("User manual. The manual is written in English so "
                                  "that every user reads the same text."))
    chs = docs.chapters()
    titles = [c[0] for c in chs]
    cur = st.session_state.get("doc_chapter", titles[0])
    if cur not in titles:
        cur = titles[0]
    left, right = st.columns([1, 3.2], gap="large")
    with left:
        with st.container(key="doc_toc"):
            for i, ttl in enumerate(titles):
                if st.button(ttl, key=f"doc_{i}", width="stretch",
                             type="primary" if ttl == cur else "tertiary"):
                    st.session_state["doc_chapter"] = ttl
                    st.rerun()
        st.download_button(t("Download the manual (Markdown)"),
                           data=lambda: docs.manual_text().encode("utf-8"),
                           file_name="GeoChem_App_user_manual.md", mime="text/markdown",
                           on_click="ignore", icon=":material/download:")
    with right:
        k = titles.index(cur)
        body = chs[k][1]
        with st.container(key="doc_body"):
            st.markdown(f"## {cur}")
            st.markdown(docs.embed_images(body), unsafe_allow_html=True)
        nav_l, nav_r = st.columns(2)
        if k > 0 and nav_l.button(":material/arrow_back: " + titles[k - 1], key="doc_prev"):
            st.session_state["doc_chapter"] = titles[k - 1]
            st.rerun()
        if k < len(titles) - 1 and nav_r.button(titles[k + 1] + " :material/arrow_forward:",
                                                key="doc_next"):
            st.session_state["doc_chapter"] = titles[k + 1]
            st.rerun()


def page_references():
    header(t("References"), t("Scientific sources of every diagram, calculation and "
                              "data set in the app. Please cite them in your work."))
    q = st.text_input(t("Search"), placeholder=t("Search author, year or diagram"),
                      label_visibility="collapsed", key="ref_search").lower()
    refs = docs.diagram_references()
    left, right = st.columns(2, gap="large")
    with left:
        st.markdown(f"#### {t('Diagrams')}")
        for cat, rows in refs.items():
            rows = [r for r in rows if not q or q in (r[0] + r[1]).lower()]
            if not rows:
                continue
            st.markdown(f'<p class="gc-nav-head" style="margin-left:0">{t(cat)}</p>',
                        unsafe_allow_html=True)
            for ttl, ref, src in rows:
                st.markdown(f'<p class="gc-ref"><b>{ttl}</b><br>{ref}'
                            + (f'<br><span>{t("Boundaries")}: {src}</span>' if src else "")
                            + "</p>", unsafe_allow_html=True)
    with right:
        st.markdown(f"#### {t('Calculations, data and software')}")
        for what, ref in docs.GENERAL:
            if q and q not in (what + ref).lower():
                continue
            st.markdown(f'<p class="gc-ref"><b>{t(what)}</b><br>{ref}</p>',
                        unsafe_allow_html=True)
        st.markdown(f"#### {t('Open-source libraries')}")
        st.dataframe(pd.DataFrame(docs.LIBRARIES, columns=[t("Library"), t("Used for"),
                                                           t("License")]),
                     hide_index=True)
        st.download_button(t("Download all references (TXT)"),
                           data=lambda: docs.references_text().encode("utf-8"),
                           file_name="GeoChem_App_references.txt", mime="text/plain",
                           on_click="ignore", icon=":material/download:")


def page_about():
    header(t("About"))
    st.markdown(f'<div class="gc-hero">{docs.logo(64, DARK)}<div><h2>GeoChem App</h2>'
                f'<p>{t("A free, open-source web application for whole-rock geochemistry")}'
                f' &middot; {t("version")} {APP_VERSION}</p></div></div>',
                unsafe_allow_html=True)
    a, b = st.columns(2, gap="large")
    with a:
        with st.container(border=True):
            st.markdown(f"**{t('Purpose')}**")
            st.markdown(t("GeoChem App brings the diagrams of GCDkit to a simple web "
                          "interface, so that students and researchers, also those with "
                          "limited funding or no programming background, can plot and "
                          "check their geochemical data with confidence."))
        with st.container(border=True):
            st.markdown(f"**{t('Developer')}**")
            st.markdown(f"{DEVELOPER}  \n[{DEVELOPER_EMAIL}](mailto:{DEVELOPER_EMAIL})  \n"
                        + t("Hokkaido University, Japan"))
            st.markdown(f":material/public: [{APP_URL}]({APP_URL})  \n"
                        f":material/code: [{REPO_URL}]({REPO_URL})")
            st.caption(t("Bug reports, diagram requests and translations are welcome by "
                         "e-mail. Please attach a screenshot and, if possible, a small "
                         "example file."))
        with st.container(border=True):
            st.markdown(f"**{t('License')}**")
            st.markdown(t("GNU General Public License v3.0 (GPL-3.0). You may use, study, "
                          "share and change the app. A shared, changed version must stay "
                          "under the GPL and keep the credits."))
    with b:
        with st.container(border=True):
            st.markdown(f"**{t('How to cite')}**")
            st.code(f"Hidayah B. (2026) GeoChem App: a free web application for "
                    f"whole-rock geochemistry, version {APP_VERSION}. "
                    f"{APP_URL}\n\n"
                    "Janousek V., Farrow C.M., Erban V. (2006) Interpretation of "
                    "whole-rock geochemical data in igneous geochemistry: introducing "
                    "Geochemical Data Toolkit (GCDkit). Journal of Petrology 47(6), "
                    "1255-1259.", language=None, wrap_lines=True)
            st.caption(t("Also cite the original reference of every diagram you used "
                         "(see References)."))
        with st.container(border=True):
            st.markdown(f"**{t('Acknowledgements')}**")
            st.markdown(t("Diagram boundaries and the CIPW norm are converted from GCDkit "
                          "6.3 by V. Janousek, C.M. Farrow, V. Erban and co-authors (GPL). "
                          "The XRF module follows Mikuni, Ishikawa and Sato (2025, CC BY "
                          "4.0). Built with Streamlit, pandas, NumPy and Matplotlib."))
        with st.expander(t("What is new (changelog)")):
            if docs.CHANGELOG.exists():
                st.markdown(re.sub(r"^# .*\n", "", docs.CHANGELOG.read_text(encoding="utf-8")))


PAGES = {
    "dashboard": st.Page(page_dashboard, title=t("Dashboard"),
                         icon=":material/space_dashboard:", default=True, url_path="dashboard"),
    "data": st.Page(page_data, title=t("Data"), icon=":material/table_chart:", url_path="data"),
    "diagrams": st.Page(page_diagrams, title=t("Diagrams"), icon=":material/category:",
                        url_path="diagrams"),
    "spider": st.Page(page_spider, title=t("Spider diagrams"), icon=":material/show_chart:",
                      url_path="spider"),
    "xy": st.Page(page_xy, title=t("XY plot"), icon=":material/scatter_plot:", url_path="xy"),
    "stats": st.Page(page_stats, title=t("Statistics"), icon=":material/bar_chart:",
                     url_path="statistics"),
    "symbols": st.Page(page_symbols, title=t("Symbols and colours"),
                       icon=":material/palette:", url_path="symbols"),
    "appearance": st.Page(page_appearance, title=t("Plot appearance"),
                          icon=":material/format_size:", url_path="appearance"),
    "settings": st.Page(page_settings, title=t("Settings"), icon=":material/tune:",
                        url_path="settings"),
    "xrfqc": st.Page(page_xrfqc, title=t("XRF quality control"),
                     icon=":material/fact_check:", url_path="xrf-qc"),
    "docs": st.Page(page_docs, title=t("Documentation"), icon=":material/menu_book:",
                    url_path="docs"),
    "references": st.Page(page_references, title=t("References"),
                          icon=":material/library_books:", url_path="references"),
    "about": st.Page(page_about, title=t("About"), icon=":material/info:",
                     url_path="about"),
}
NAV_GROUPS = [("Overview", ["dashboard", "data"]),
              ("Plots", ["diagrams", "spider", "xy"]),
              ("Tools", ["stats"] + (["xrfqc"] if settings["xrf_qc"] else [])
               + ["symbols", "appearance", "settings"])]
nav = st.navigation([p for k, p in PAGES.items() if k != "xrfqc" or settings["xrf_qc"]],
                    position="hidden")

# ---- top bar: brand, documentation, references, about, language, theme ----
def _set_lang():
    st.session_state["lang"] = st.session_state["lang_pick"]


def _set_theme():
    st.session_state["theme_choice"] = st.session_state["theme_pick"]
    st.session_state["_apply_theme"] = True


if st.session_state.get("lang_pick") != st.session_state["lang"]:
    st.session_state["lang_pick"] = st.session_state["lang"]
if st.session_state.get("theme_pick") != choice:
    st.session_state["theme_pick"] = choice
with st.container(key="gc_topbar"):
    brand, acts = st.columns([1, 2.7], gap="small", vertical_alignment="center")
    brand.markdown(f'<div class="gc-top-brand">{docs.logo(36, DARK)}<div><b>GeoChem App'
                   f'<span class="gc-ver">v{APP_VERSION}</span></b>'
                   f'<small>{t("Whole-rock geochemistry")}</small>'
                   f'</div></div>', unsafe_allow_html=True)
    row = acts.container(horizontal=True, horizontal_alignment="right", gap="small",
                         vertical_alignment="center")
    row.page_link(PAGES["docs"], label=t("Documentation"), icon=":material/menu_book:",
                  width="content")
    row.page_link(PAGES["references"], label=t("References"),
                  icon=":material/library_books:", width="content")
    row.page_link(PAGES["about"], label=t("About"), icon=":material/info:", width="content")
    with row.popover(LANG_SHORT[st.session_state["lang"]], icon=":material/translate:",
                     help=t("Language"), width="content"):
        st.radio(t("Language"), list(LANGUAGES), format_func=LANGUAGES.get,
                 key="lang_pick", on_change=_set_lang)
    with row.popover(t(choice), icon=THEME_ICON[choice], help=t("Theme"), width="content"):
        st.radio(t("Theme"), THEME_CHOICES, format_func=t, key="theme_pick",
                 on_change=_set_theme, label_visibility="collapsed")

# ---- sidebar: navigation + display options ----
for head, keys in NAV_GROUPS:
    st.sidebar.markdown(f'<p class="gc-nav-head">{t(head)}</p>', unsafe_allow_html=True)
    for k in keys:
        st.sidebar.page_link(PAGES[k])

if ctx is not None:
    st.sidebar.markdown(f'<p class="gc-nav-head">{t("Display")}</p>', unsafe_allow_html=True)
    text_cols = ctx["std"].select_dtypes(exclude="number").columns.tolist()
    if st.session_state.get("group_col") not in [NONE] + text_cols:
        st.session_state["group_col"] = NONE
    if st.session_state.get("label_col") not in [NONE] + text_cols:
        st.session_state["label_col"] = NONE
    st.sidebar.selectbox(t("Group samples by"), [NONE] + text_cols, key="group_col",
                         format_func=lambda v: t(v) if v == NONE else v)
    gsel = st.session_state.get("group_col", NONE)
    if gsel != NONE:
        all_groups = group_names(gsel)
        if not set(st.session_state.get("group_keep") or []) <= set(all_groups):
            st.session_state.pop("group_keep", None)
        st.sidebar.multiselect(t("Show groups"), all_groups, default=all_groups,
                               key="group_keep")
    else:
        st.session_state.pop("group_keep", None)
    st.sidebar.selectbox(t("Label points with"), [NONE] + text_cols, key="label_col",
                         format_func=lambda v: t(v) if v == NONE else v)
    st.sidebar.page_link(PAGES["symbols"], label=t("Edit symbols and colours"),
                         icon=":material/palette:")

st.sidebar.markdown(
    f'<div class="gc-credit">{t("Developed by")} <b>{DEVELOPER}</b><br>'
    f'<a href="mailto:{DEVELOPER_EMAIL}">{DEVELOPER_EMAIL}</a><br>'
    f'GeoChem App {APP_VERSION}, GPL-3.0</div>', unsafe_allow_html=True)

# A theme change: Streamlit keeps the theme per page address, so it is stored
# for every page of the app, then the page reloads (session restored by ?s=...).
if st.session_state.pop("_apply_theme", False):
    _paths = ["/"] + ["/" + pg.url_path for pg in PAGES.values()]
    st.html(f"""<script>
      const v = JSON.stringify('{choice}');
      const paths = {_paths!r};
      paths.forEach(p => localStorage.setItem('stActiveTheme-' + p + '-v2', v));
      Object.keys(localStorage).filter(k => k.startsWith('stActiveTheme-'))
            .forEach(k => localStorage.setItem(k, v));
      window.parent.location.reload();
    </script>""", unsafe_allow_javascript=True)

nav.run()

# remember this session's state, so a reload (theme change) restores it
_mem = _store()
_mem[token] = {k: (st.session_state[k] if k != "settings" else
                   {a: b for a, b in st.session_state[k].items() if not a.startswith("_")})
               for k in STATE_KEYS if k in st.session_state}
_mem.move_to_end(token)
while len(_mem) > MAX_SESSIONS:
    _mem.popitem(last=False)
