# tools/gcdkit_import.py
# Converts GCDkit diagram templates (R, "Figaro" format) into JSON geometry
# used by GeoChem App. GCDkit: Janousek, Farrow and Erban (2006), GPL >= 2.
# The output keeps GCDkit's coordinates unchanged; only the format changes.
#
# Usage: python tools/gcdkit_import.py <GCDkit/Diagrams folder> <output folder>

import json
import math
import re

import numpy as np
import sys
from pathlib import Path

# id: (relative file, options)
FILES = {
    "TAS": ("Classification/English/TAS.r", {}),
    "AFM": ("Classification/English/AFM.r", {"keep": "else"}),
    "PeceTaylor": ("Classification/English/PeceTaylor.r", {}),
    "Miyashiro": ("Classification/English/Miyashiro.r", {}),
    "Shand": ("Classification/English/Shand.r", {}),
    "MiddlemostPlut": ("Classification/English/MiddlemostPlut.r", {}),
    "Pearce1996": ("Classification/English/Pearce1996.r", {}),
    "Hastie": ("Classification/English/Hastie.r", {}),
    "Jensen": ("Classification/English/Jensen.r", {}),
    "Frost_2008": ("Geotectonic/Frost_2008.r", {}),
    "PearceNbThYb": ("Geotectonic/PearceNbThYb.r", {}),
    "PearceNbTiYb": ("Geotectonic/PearceNbTiYb.r", {}),
    "PearceGranite": ("Geotectonic/PearceGranite.r", {}),
    "Whalen": ("Geotectonic/Whalen.r", {}),
    "LaYb": ("Geotectonic/LaYb.r", {}),
    "Cann": ("Geotectonic/Cann.r", {}),
    "Meschede": ("Geotectonic/Meschede.r", {}),
    "Wood": ("Geotectonic/Wood.r", {}),
    "Shervais": ("Geotectonic/Shervais.r", {}),
    "Saccani": ("Geotectonic/Saccani.r", {}),
    "Paulick": ("User/Paulick.r", {}),
    # stage 2
    "LarocheVolc": ("Classification/English/LarocheVolc.r", {}),
    "LarochePlut": ("Classification/English/LarochePlut.r", {}),
    "Batchelor": ("Geotectonic/Batchelor.r", {}),
    "Agrawal": ("Geotectonic/Agrawal.r", {}),
    "Verma": ("Geotectonic/Verma.r", {}),
    "OhtaArai": ("Geotectonic/OhtaArai.r", {}),
}


# ---------------- R text helpers ----------------
def strip_comments(text):
    out = []
    for line in text.splitlines():
        s, q = [], None
        for ch in line:
            if q:
                s.append(ch)
                if ch == q:
                    q = None
            elif ch in "\"'":
                q = ch
                s.append(ch)
            elif ch == "#":
                break
            else:
                s.append(ch)
        out.append("".join(s))
    return "\n".join(out)


def match_bracket(text, i, open_ch="(", close_ch=")"):
    """Index of the bracket that closes text[i] (which is open_ch)."""
    depth, q = 0, None
    for j in range(i, len(text)):
        ch = text[j]
        if q:
            if ch == q and text[j - 1] != "\\":
                q = None
            continue
        if ch in "\"'":
            q = ch
        elif ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                return j
    raise ValueError("unbalanced")


def drop_branch(text, which):
    """Remove 'else' branches (which='else') or the 'if' branch preceding
    an else (which='if'), so that the default code path remains."""
    out, i = [], 0
    pat = re.compile(r"\belse\b")
    while True:
        m = pat.search(text, i)
        if not m:
            out.append(text[i:])
            break
        j = m.end()
        while j < len(text) and text[j] in " \t\n":
            j += 1
        if which == "else":
            out.append(text[i:m.start()])
            if j < len(text) and text[j] == "{":
                i = match_bracket(text, j, "{", "}") + 1
            else:                       # single statement until end of line
                k = text.find("\n", j)
                i = len(text) if k < 0 else k
        else:                           # keep else: blank the preceding if block
            before = text[i:m.start()]
            k = before.rstrip().rfind("}")
            if k >= 0:
                # find start of matching '{'
                depth = 0
                for p in range(k, -1, -1):
                    if before[p] == "}":
                        depth += 1
                    elif before[p] == "{":
                        depth -= 1
                        if depth == 0:
                            before = before[:p] + "{}"
                            break
            out.append(before)
            i = j
    return "".join(out)


def to_python(expr):
    """Translate a (simple) R expression into Python source."""
    res, i, q = [], 0, None
    while i < len(expr):
        ch = expr[i]
        if q:
            res.append(ch)
            if ch == q and expr[i - 1] != "\\":
                q = None
            i += 1
            continue
        if ch in "\"'":
            q = ch
            res.append(ch)
            i += 1
            continue
        n = re.match(r"(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?(:(\d+))?", expr[i:])
        if n and not (res and re.match(r"[A-Za-z0-9_]", res[-1][-1:] or " ")):
            if n.group(3):                       # R range a:b
                a = int(float(n.group(1)))
                res.append(f"RANGE({a},{n.group(4)})")
            else:
                res.append(n.group(1) + (n.group(2) or ""))
            i += len(n.group(0))
            continue
        m = re.match(r"(?:[A-Za-z_]|\.[A-Za-z_])[A-Za-z0-9_.:]*", expr[i:])
        if m:
            w = m.group(0)
            rep = {"c": "C", "list": "L", "TRUE": "True", "FALSE": "False",
                   "T": "True", "F": "False", "NA": "None", "NULL": "None",
                   "GCDkit::annotate": "ANN", "annotate": "ANN",
                   "paste": "PASTE", "log10": "LOG10", "sqrt": "SQRT",
                   "rep": "REP", "seq": "SEQ"}.get(w)
            if rep is None:
                rep = w.replace("::", "__").replace(".", "_")
            res.append(rep)
            i += len(w)
            continue
        if expr.startswith("^", i):
            res.append("**")
            i += 1
            continue
        if expr.startswith("[[", i):          # plate[[1]] -> plate_1
            j = expr.index("]]", i)
            res.append("_" + expr[i + 2:j])
            i = j + 2
            continue
        res.append(ch)
        i += 1
    return "".join(res)


class NS(dict):
    def __missing__(self, key):
        return None


def flat(args):
    out = []
    for a in args:
        if isinstance(a, np.ndarray):
            out.extend(a.tolist())
        elif isinstance(a, (list, tuple)):
            out.extend(flat(a))
        elif a is not None:
            out.append(a)
    return out


def C(*args):
    if args and all(isinstance(a, dict) or a is None for a in args):
        d = {}
        for a in args:
            if a:
                d.update(a)
        return d
    v = flat(args)
    if v and all(isinstance(x, (int, float, np.floating, np.integer)) for x in v):
        return np.array(v, dtype=float)
    return v


def L(*args, **kw):
    d = dict(kw)
    if args:
        d["_type"] = args[0]
    d["_order"] = list(kw)
    return d


def vec(f):
    def g(x):
        if isinstance(x, list):
            return [f(v) for v in x]
        return f(x)
    return g


BASE = {"NAMED": lambda v, n: dict(zip(n, flat([v]))), "list": list, "range": range, "C": C, "L": L, "ANN": lambda *a: "".join(str(x) for x in a),
        "PASTE": lambda *a, **k: " ".join(str(x) for x in a),
        "LOG10": np.log10, "SQRT": np.sqrt,
        "RANGE": lambda a, b: np.arange(a, b + 1, dtype=float),
        "SEQ": lambda a, b, by=1, **k: np.arange(a, b + by / 2, by),
        "REP": lambda x, n=1, **k: [x] * int(n),
        "plt_col": ["col0", "col1", "col2", "col3", "col4"],
        "col1": "col1", "col2": "col2", "True": True, "False": False,
        "getOption": lambda *a: True, "names": lambda *a: None}


def evaluate(text, keep="if"):
    """Evaluate the assignments of an R diagram function in order.
    Returns the namespace (sheet, plate_1 ... and helper variables)."""
    body = strip_comments(text.replace("\r", ""))
    if keep == "if":
        body = drop_branch(body, "else")
    else:
        # keep the else branch of the FIRST if/else only (e.g. AFM equ=FALSE)
        m = re.search(r"\belse\b", body)
        j = m.end()
        while body[j] in " \t\n":
            j += 1
        end = match_bracket(body, j, "{", "}") + 1 if body[j] == "{" else body.find("\n", j)
        body = drop_branch(body[:end], "if") + drop_branch(body[end:], "else")
    body = re.sub(r"(\n\s*)template\s*=\s*list\(", r"\1template<-list(", body)
    # top-level "name=list(" (no indentation) is an assignment too
    body = re.sub(r"(?m)^([A-Za-z_][\w.]*)\s*=\s*list\(", r"\1<-list(", body)
    # plotmath labels such as expression(paste(plain(R[1]), ...)) -> ""
    while "expression(" in body:
        i = body.index("expression(")
        j = match_bracket(body, i + len("expression"))
        body = body[:i] + '""' + body[j + 1:]
    # names(X) <- c("a", "b") turns a vector into a named lookup
    body = re.sub(r"names\(([A-Za-z_.][\w.]*)\)\s*<-\s*",
                  lambda m: f"{m.group(1)}<-NAMED({m.group(1)}, ", body)
    body = re.sub(r"(NAMED\([^,]+, c\([^)]*\))", r"\1)", body)
    # R tolerates repeated element names inside list(); make them unique
    counter = iter(range(10 ** 6))
    body = re.sub(r"\b([A-Za-z]\w*)(\s*=\s*list\()",
                  lambda m: f"{m.group(1)}__{next(counter)}{m.group(2)}", body)
    ns = NS(BASE)
    # default values of the function arguments, e.g. function(xmin=0.1, ...)
    fm = re.search(r"function\s*\(", body)
    if fm:
        k = match_bracket(body, fm.end() - 1)
        for arg in re.split(r",(?![^()]*\))", body[fm.end():k]):
            if "=" in arg:
                key, val = arg.split("=", 1)
                try:
                    ns[to_python(key.strip())] = eval(to_python(val.strip()),
                                                      {"__builtins__": {}}, ns)
                except Exception:
                    pass
    for m in re.finditer(r"(?<![$\w.\]])([A-Za-z_.][A-Za-z0-9_.]*(?:\[\[\d+\]\])?)\s*<<?-\s*", body):
        name = to_python(m.group(1))
        start = m.end()
        # expression ends at end of line, unless brackets are open
        j, depth, q = start, 0, None
        while j < len(body):
            ch = body[j]
            if q:
                if ch == q and body[j - 1] != "\\":
                    q = None
            elif ch in "\"'":
                q = ch
            elif ch in "([{":
                depth += 1
            elif ch in ")]}":
                if depth == 0:
                    break
                depth -= 1
            elif ch in "\n;" and depth == 0:
                break
            j += 1
        expr = body[start:j].strip()
        if not expr or expr.startswith("function"):
            continue
        py = to_python(expr)
        try:
            ns[name] = eval(py, {"__builtins__": {}}, ns)
        except SyntaxError:
            # R allows repeated arguments (e.g. main= or cex= twice); keep the first
            py = re.sub(r',\s*main\s*=\s*""', "", py)
            prev = None
            while prev != py:
                prev = py
                py = re.sub(r"\b(\w+)=([^,()]+),(\s*)\1=[^,()]+", r"\1=\2", py)
            try:
                ns[name] = eval(py, {"__builtins__": {}}, ns)
            except Exception:
                pass
        except Exception:
            pass
    return ns


# ---------------- geometry extraction ----------------
def colour_role(col):
    if col in (None, "col2", "col1"):
        return "line"
    if col == "col3":
        return "minor"
    return "line"


def nums(v):
    if v is None or isinstance(v, dict):
        return None
    try:
        return [float(x) for x in flat([v])]
    except (TypeError, ValueError):
        return None


def panel_from_sheet(demo):
    demo = {k.split("__")[0]: v for k, v in demo.items()}
    call = {k.split("__")[0]: v for k, v in (demo.get("call") or {}).items()
            if not k.startswith("_")}
    tmpl = {k.split("__")[0] if k.split("__")[0] in ("GCDkit", "A", "B", "C", "clssf")
            else k: v for k, v in (demo.get("template") or {}).items()}
    order = [k for k in tmpl if not k.startswith("_")]
    log = str(call.get("log") or "")
    out = {"xlim": nums(call.get("xlim")), "ylim": nums(call.get("ylim")),
           "log_x": "x" in log, "log_y": "y" in log,
           "xlab": call.get("xlab") or "", "ylab": call.get("ylab") or "",
           "title": call.get("main") or "", "ternary": False,
           "lines": [], "polygons": [], "texts": [], "fields": []}
    clssf = tmpl.get("clssf")
    use_idx, names = [], []
    if clssf:
        use_idx = [int(i) for i in flat([clssf.get("use")])]
        names = flat([clssf.get("rcname")])
    for k, el in tmpl.items():
        if k.startswith("_") or not isinstance(el, dict):
            continue
        t = el.get("_type")
        if k == "GCDkit":
            out["ternary"] = el.get("plot_type") == "ternary"
            out["name"] = el.get("plot_name")
            continue
        if t == "lines" and el.get("x") is not None:
            out["lines"].append({"x": nums(el["x"]), "y": nums(el["y"]),
                                 "lwd": float(el.get("lwd") or 1),
                                 "dash": el.get("lty") in ("dashed", 2, "dotted"),
                                 "role": colour_role(el.get("col"))})
        elif t == "polygon":
            out["polygons"].append({"x": nums(el["x"]), "y": nums(el["y"])})
        elif t == "abline":
            ab = {k2: el.get(k2) for k2 in ("a", "b", "h", "v")}
            out["lines"].append({"abline": {k2: (float(v) if v is not None else None)
                                            for k2, v in ab.items()},
                                 "dash": el.get("lty") in ("dashed", 2, "dotted"),
                                 "role": colour_role(el.get("col"))})
        elif t == "points" and el.get("x") is not None:
            out.setdefault("points", []).append({"x": nums(el["x"]), "y": nums(el["y"])})
        elif t == "text" and k not in ("A", "B", "C") and \
                flat([el.get("x")]) and flat([el.get("y")]) and \
                len(flat([el.get("text")])) > 1:
            for tx, ty, tt in zip(flat([el["x"]]), flat([el["y"]]), flat([el["text"]])):
                out["texts"].append({"x": float(tx), "y": float(ty), "text": str(tt),
                                     "rot": float(el.get("srt") or 0),
                                     "size": float(el.get("cex") or 1),
                                     "adj": flat([el.get("adj")])[0] if el.get("adj") is not None else 0.5,
                                     "role": colour_role(el.get("col"))})
        elif t == "text" and k not in ("A", "B", "C") and \
                flat([el.get("x")]) and flat([el.get("y")]):
            out["texts"].append({"x": float(flat([el["x"]])[0]),
                                 "y": float(flat([el["y"]])[0]),
                                 "text": str(el.get("text")),
                                 "rot": float(el.get("srt") or 0),
                                 "size": float(el.get("cex") or 1),
                                 "adj": flat([el.get("adj")])[0] if el.get("adj") is not None else 0.5,
                                 "role": colour_role(el.get("col"))})
        elif t == "text" and k in ("A", "B", "C"):
            out.setdefault("apices", {})[k] = str(el.get("text"))
    # classification polygons: list positions referenced by clssf$use
    # (position 1 is clssf itself)
    for pos, name in zip(use_idx, names):
        key = order[pos - 1] if pos - 1 < len(order) else None
        el = tmpl.get(key) if key else None
        if el and el.get("x") is not None:
            out["fields"].append({"name": str(name), "x": nums(el["x"]),
                                  "y": nums(el["y"])})
    return out


def first(d, key):
    for k, v in d.items():
        if k.split("__")[0] == key:
            return v
    return {}


def import_file(path, keep="if"):
    ns = evaluate(Path(path).read_text(encoding="latin-1"), keep)
    panels = []
    if ns.get("sheet"):
        panels.append(panel_from_sheet(first(ns["sheet"], "demo")))
    i = 1
    while ns.get(f"plate_{i}"):
        panels.append(panel_from_sheet(first(ns[f"plate_{i}"], "demo")))
        i += 1
    return panels


if __name__ == "__main__":
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    dst.mkdir(parents=True, exist_ok=True)
    for did, (rel, opt) in FILES.items():
        panels = import_file(src / rel, opt.get("keep", "if"))
        info = {"id": did, "source": f"GCDkit 6.3, Diagrams/{rel}",
                "panels": panels}
        (dst / f"{did}.json").write_text(json.dumps(info, indent=1))
        print(f"{did:15s} panels={len(panels)} "
              + " | ".join(f"lines={len(p['lines'])} fields={len(p['fields'])} "
                           f"texts={len(p['texts'])}" for p in panels))
