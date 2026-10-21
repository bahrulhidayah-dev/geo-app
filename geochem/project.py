# geochem/project.py
# Project files and the work folder.
#
# A project file (*.geochem) is a ZIP archive that holds:
#   project.json   - app version, date, and the session: column setup,
#                    settings, symbols, plot appearance, grouping, labels,
#                    chosen diagram ...
#   data/<file>    - the data file exactly as it was loaded
#   xrf/<file>     - the XRF intensity file, if one was loaded
# so that a whole analysis can be saved, sent to a colleague and opened again.
#
# The work folder (desktop and portable versions only) is a normal folder on
# the user's computer with three subfolders:
#   data/      data files to open without uploading
#   exports/   figures and tables saved from the app
#   projects/  project files
# The chosen folder is remembered in ~/.geochem_app/config.json.
# Part of GeoChem App (GPL-3.0).

import io
import json
import re
import zipfile
from datetime import datetime
from pathlib import Path

EXTENSION = ".geochem"
FORMAT = 1
SUBFOLDERS = ("data", "exports", "projects")
DATA_TYPES = (".csv", ".xlsx", ".xls")
CONFIG = Path.home() / ".geochem_app" / "config.json"

# session keys stored in a project (the data files are stored separately)
STATE_KEYS = ["settings", "symbols", "appearance", "col_setups", "group_col",
              "group_keep", "label_col", "diagram_id", "lang", "spider_group",
              "spider_norm", "ternary", "variation"]


# ---------------- project files ----------------
def _jsonable(value):
    """Settings may hold caches or tuples; keep only what JSON can store."""
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items() if not str(k).startswith("_")}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def pack(state, dataset=None, xrf=None, app_version=""):
    """Project file as bytes. dataset and xrf: (file name, bytes) or None."""
    meta = {"format": FORMAT, "app": "GeoChem App", "app_version": app_version,
            "saved": datetime.now().isoformat(timespec="seconds"),
            "state": {k: _jsonable(state[k]) for k in STATE_KEYS if k in state}}
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        if dataset:
            meta["dataset"] = dataset[0]
            z.writestr("data/" + dataset[0], dataset[1])
        if xrf:
            meta["xrf"] = xrf[0]
            z.writestr("xrf/" + xrf[0], xrf[1])
        z.writestr("project.json", json.dumps(meta, indent=2, ensure_ascii=False))
    return buf.getvalue()


def unpack(content):
    """Read a project file. Returns (meta, dataset, xrf); dataset and xrf are
    (file name, bytes) or None. Raises ValueError for a wrong file."""
    try:
        z = zipfile.ZipFile(io.BytesIO(content))
        meta = json.loads(z.read("project.json"))
    except (zipfile.BadZipFile, KeyError, ValueError) as e:
        raise ValueError("not a GeoChem App project file") from e
    if meta.get("app") != "GeoChem App":
        raise ValueError("not a GeoChem App project file")
    dataset = xrf = None
    if meta.get("dataset"):
        dataset = (meta["dataset"], z.read("data/" + meta["dataset"]))
    if meta.get("xrf"):
        xrf = (meta["xrf"], z.read("xrf/" + meta["xrf"]))
    return meta, dataset, xrf


def safe_name(name, default="project"):
    """A file name without characters that Windows or macOS refuse."""
    name = re.sub(r'[\\/:*?"<>|]+', "_", str(name)).strip(" .")
    return name or default


# ---------------- work folder ----------------
def default_folder():
    docs = Path.home() / "Documents"
    return (docs if docs.exists() else Path.home()) / "GeoChem App"


def load_config():
    try:
        return json.loads(CONFIG.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_config(cfg):
    try:
        CONFIG.parent.mkdir(parents=True, exist_ok=True)
        CONFIG.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    except OSError:
        pass                         # remembering is a convenience only


def prepare(folder):
    """Create the folder and its subfolders. Returns the resolved Path.
    Raises OSError when the folder cannot be created or written."""
    p = Path(folder).expanduser()
    for sub in SUBFOLDERS:
        (p / sub).mkdir(parents=True, exist_ok=True)
    test = p / "exports" / ".write_test"
    test.write_text("ok")
    test.unlink()
    return p.resolve()


def remember(folder):
    cfg = load_config()
    recent = [str(folder)] + [f for f in cfg.get("recent", []) if f != str(folder)]
    cfg.update({"work_folder": str(folder), "recent": recent[:6]})
    save_config(cfg)


def forget():
    cfg = load_config()
    cfg.pop("work_folder", None)
    save_config(cfg)


def list_files(folder, sub, suffixes):
    """Files in folder/sub (newest first) as (name, size kB, modified)."""
    d = Path(folder) / sub
    if not d.is_dir():
        return []
    files = [f for f in d.iterdir() if f.is_file() and f.suffix.lower() in suffixes]
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    return [(f.name, round(f.stat().st_size / 1024, 1),
             datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M"))
            for f in files]


def write(folder, sub, name, content):
    """Write bytes to folder/sub/name. Returns the full path."""
    p = Path(folder) / sub / safe_name(name)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(content)
    return p


def read(folder, sub, name):
    return (Path(folder) / sub / safe_name(name)).read_bytes()
