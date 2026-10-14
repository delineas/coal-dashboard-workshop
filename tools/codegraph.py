#!/usr/bin/env python3
"""Code graph of this repository in SQLite. Run `tools/codegraph.py build`, then `tools/codegraph.py help`."""
import ast
import os
import re
import sqlite3
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / ".codegraph" / "graph.sqlite"
LIMIT = 40
SHOW_LIMIT = 60
HTTP = {"get", "post", "put", "patch", "delete"}
TS_SUFFIXES = (".ts", ".tsx")

TABLES = {
    "symbols": "file, name, kind, start_line, end_line",
    "imports": "file, line, name, source, target",
    "refs": "file, line, symbol, name, kind",
    "endpoints": "file, line, method, path, symbol",
    "api_urls": "file, line, url, symbol",
    "routes": "file, line, path, component",
    "sql_refs": "file, line, symbol, table_name, mode",
    "tests_hit": "file, line, symbol, method, url",
}

TS_DECL = re.compile(r"^(?:export\s+)?(?:default\s+)?(?:async\s+)?(function|class|interface|type|enum|const|let)\s+(\w+)", re.M)
TS_IMPORT = re.compile(r"^import\s+(?:type\s+)?(?P<clause>[^;'\"]*?)\s+from\s+['\"](?P<src>[^'\"]+)['\"]", re.M)
TS_ROUTE = re.compile(r"<Route\s+path=\"([^\"]+)\"\s+element=\{<(\w+)")
TS_URL = re.compile(r"([`'\"])((?:/api/|\$\{\w+\})[^`'\"]*)\1")
TS_URL_CONST = re.compile(r"^(?:export\s+)?const\s+(\w+)\s*=\s*(['\"])(/api/[^'\"]*)\2", re.M)
TS_CALL_TAIL = re.compile(r"\s*(?:<[^>()]*>)?\(")
SQL = {
    "read": re.compile(r"\b(?:FROM|JOIN)\s+(\w+)"),
    "write": re.compile(r"\bINSERT\s+INTO\s+(\w+)"),
    "define": re.compile(r"\bCREATE\s+(?:TABLE|VIEW)\s+(\w+)"),
}


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def decl_end(text, pos):
    """Return the index of the newline that ends the declaration which starts before `pos`."""
    depth, i, n = 0, pos, len(text)
    while i < n:
        c = text[i]
        if c in "'\"`":
            i += 1
            while i < n and text[i] != c and (c == "`" or text[i] != "\n"):
                i += 2 if text[i] == "\\" else 1
        elif text.startswith("//", i):
            i = text.find("\n", i) if "\n" in text[i:] else n
            continue
        elif text.startswith("/*", i):
            i = text.find("*/", i) + 1 or n
        elif c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
        elif c == "\n" and depth == 0 and not continues(text, i):
            return i
        i += 1
    return n


def continues(text, newline):
    if text[:newline].rstrip().endswith(("=>", "=", ",", "|", "&", "+", "?", ":")):
        return True
    return text[newline:].lstrip()[:1] in ("|", "&", "?", ":", ".", "+")


def ts_symbols(text):
    out = []
    for m in TS_DECL.finditer(text):
        kind, name = m.groups()
        out.append((name, "const" if kind == "let" else kind, line_of(text, m.start()), line_of(text, decl_end(text, m.end()))))
    return out


def py_symbols(tree):
    out = []

    def span(node):
        return min([d.lineno for d in node.decorator_list] + [node.lineno]), node.end_lineno

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out.append((node.name, "function", *span(node)))
        elif isinstance(node, ast.ClassDef):
            out.append((node.name, "class", *span(node)))
            out += [(f"{node.name}.{m.name}", "method", *span(m)) for m in node.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))]
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            out += [(t.id, "const", node.lineno, node.end_lineno) for t in targets if isinstance(t, ast.Name)]
    return out


def enclosing(symbols, line):
    hits = [s for s in symbols if s[2] <= line <= s[3]]
    return min(hits, key=lambda s: s[3] - s[2])[0] if hits else "<module>"


def resolve_py(file, level, module, name, files):
    parts = module.split(".") if module else []
    bases = [Path(file).parents[level - 1]] if level else [Path("."), Path("backend")]
    for base in bases:
        for rel in ([*parts, name] if name else [], parts):
            if not rel:
                continue
            stem = base.joinpath(*rel).as_posix()
            for candidate in (f"{stem}.py", f"{stem}/__init__.py"):
                if candidate in files:
                    return candidate
    return None


def resolve_ts(file, spec, files):
    if not spec.startswith("."):
        return None
    stem = os.path.normpath(os.path.join(os.path.dirname(file), spec))
    return next((c for c in (f"{stem}{s}" for s in (".ts", ".tsx", "/index.ts", "/index.tsx")) if c in files), None)


def py_text(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        return "".join(v.value if isinstance(v, ast.Constant) else "{}" for v in node.values)
    return None


def sql_hits(text):
    """Yield (line offset, owning view or None, mode, table) for each SQL reference in a string."""
    hits = sorted((m.start(), mode, m.group(1)) for mode, rx in SQL.items() for m in rx.finditer(text))
    owner = None
    for pos, mode, table in hits:
        if mode == "define":
            owner = table
        yield text.count("\n", 0, pos), owner if mode == "read" else None, mode, table


def py_refs(tree, known, modules):
    called = {id(n.func) for n in ast.walk(tree) if isinstance(n, ast.Call)}

    def visit(node, shadow):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            shadow = shadow | {a.arg for a in ast.walk(node.args) if isinstance(a, ast.arg)}
            shadow = shadow | {n.id for n in ast.walk(node) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)}
        name = None
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) and node.id not in shadow:
            name = node.id
        elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id in modules:
            name = node.attr
        if name in known:
            yield node.lineno, name, "call" if id(node) in called else "ref"
        for child in ast.iter_child_nodes(node):
            yield from visit(child, shadow)

    return visit(tree, frozenset())


def scan_py(f, tree, symbols, known, files, add):
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                modules.add((a.asname or a.name).split(".")[0])
                add("imports", f, node.lineno, (a.asname or a.name).split(".")[0], a.name, resolve_py(f, 0, a.name, None, files))
        elif isinstance(node, ast.ImportFrom):
            for a in node.names:
                modules.add(a.asname or a.name)
                add("imports", f, node.lineno, a.asname or a.name, "." * node.level + (node.module or ""), resolve_py(f, node.level, node.module, a.name, files))

    decorators = set()
    for node in tree.body:
        for dec in getattr(node, "decorator_list", []):
            decorators.add(id(dec))
            if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute) and dec.func.attr in HTTP and dec.args and py_text(dec.args[0]):
                add("endpoints", f, dec.lineno, dec.func.attr.upper(), py_text(dec.args[0]), node.name)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and id(node) not in decorators and isinstance(node.func, ast.Attribute) and node.func.attr in HTTP and node.args:
            url = py_text(node.args[0])
            if url and url.startswith("/api/"):
                add("tests_hit", f, node.lineno, enclosing(symbols, node.lineno), node.func.attr.upper(), url)

    inner = {id(v) for n in ast.walk(tree) if isinstance(n, ast.JoinedStr) for v in n.values}
    kinds = {s[0]: s[1] for s in symbols}
    sql_consts = defaultdict(list)
    for node in ast.walk(tree):
        text = py_text(node) if id(node) not in inner else None
        if not text:
            continue
        for offset, owner, mode, table in sql_hits(text):
            line = node.lineno + offset
            symbol = owner or enclosing(symbols, line)
            add("sql_refs", f, line, symbol, table, mode)
            if owner is None and kinds.get(symbol) == "const" and mode != "define":
                sql_consts[symbol].append((table, mode))
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) and node.id in sql_consts:
            user = enclosing(symbols, node.lineno)
            for table, mode in sql_consts[node.id] if user != node.id else []:
                add("sql_refs", f, node.lineno, user, table, mode)

    for line, name, kind in py_refs(tree, known, modules):
        add("refs", f, line, enclosing(symbols, line), name, kind)


def scan_ts(f, text, symbols, known, files, url_consts, add):
    import_lines = set()
    for m in TS_IMPORT.finditer(text):
        line = line_of(text, m.start())
        import_lines.update(range(line, line_of(text, m.end()) + 1))
        clause = re.sub(r"[{}]", "", m["clause"])
        for part in (p for p in clause.split(",") if p.strip()):
            add("imports", f, line, part.split()[-1], m["src"], resolve_ts(f, m["src"], files))

    for m in TS_ROUTE.finditer(text):
        add("routes", f, line_of(text, m.start()), m[1], m[2])

    for m in TS_URL.finditer(text):
        url = re.sub(r"^\$\{(\w+)\}", lambda k: url_consts.get(k[1], ""), m[2])
        if url.startswith("/api/"):
            line = line_of(text, m.start())
            add("api_urls", f, line, re.sub(r"\$\{[^}]*\}", "{}", url).split("?")[0], enclosing(symbols, line))

    if not known:
        return
    names = "|".join(sorted(map(re.escape, known), key=len, reverse=True))
    for m in re.finditer(rf"(?<![\w.$/'\"`>])({names})\b", text):
        line, start = line_of(text, m.start()), m.start()
        if line in import_lines or any(s[0] == m[1] and s[2] == line for s in symbols):
            continue
        if start > 1 and text[start - 1] == "<" and not re.match(r"\w", text[start - 2]):
            kind = "render"
        else:
            kind = "call" if TS_CALL_TAIL.match(text, m.end()) else "ref"
        add("refs", f, line, enclosing(symbols, line), m[1], kind)


def build():
    listing = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.splitlines()
    sources = [f for f in listing if f.endswith((".py", *TS_SUFFIXES)) and (ROOT / f).is_file()]
    files = set(sources)
    texts = {f: (ROOT / f).read_text() for f in sources}
    trees = {f: ast.parse(t) for f, t in texts.items() if f.endswith(".py")}
    symbols = {f: py_symbols(trees[f]) if f in trees else ts_symbols(t) for f, t in texts.items()}
    known = {
        lang: {s[0] for f in sources if (f in trees) == (lang == "py") for s in symbols[f] if s[1] != "method"}
        for lang in ("py", "ts")
    }
    url_consts = {m[1]: m[3] for t in texts.values() for m in TS_URL_CONST.finditer(t)}

    rows = {t: [] for t in TABLES}

    def add(table, *row):
        rows[table].append(row)

    for f in sources:
        for symbol in symbols[f]:
            add("symbols", f, *symbol)
        if f in trees:
            scan_py(f, trees[f], symbols[f], known["py"], files, add)
        else:
            scan_ts(f, texts[f], symbols[f], known["ts"], files, url_consts, add)

    DB_PATH.parent.mkdir(exist_ok=True)
    DB_PATH.unlink(missing_ok=True)
    with sqlite3.connect(DB_PATH) as db:
        for table, columns in TABLES.items():
            db.execute(f"CREATE TABLE {table} ({columns})")
            marks = ", ".join("?" * len(columns.split(",")))
            db.executemany(f"INSERT INTO {table} VALUES ({marks})", rows[table])
    print(", ".join(f"{t}={len(r)}" for t, r in rows.items()))


def out(lines):
    for line in lines[:LIMIT]:
        print(line)
    if len(lines) > LIMIT:
        print(f"... {len(lines) - LIMIT} more")


def cmd_find(db, pattern):
    rows = db.execute("SELECT file, start_line, end_line, kind, name FROM symbols WHERE name LIKE ? ORDER BY name, file", (f"%{pattern}%",))
    out([f"{f}:{s}-{e}  {kind}  {name}" for f, s, e, kind, name in rows])


def cmd_outline(db, path):
    rows = db.execute("SELECT file, start_line, end_line, kind, name FROM symbols WHERE file LIKE ? ORDER BY file, start_line", (f"%{path}",))
    out([f"{f}:{s}-{e}  {kind}  {name}" for f, s, e, kind, name in rows])


def cmd_show(db, name, path=""):
    rows = db.execute("SELECT file, start_line, end_line FROM symbols WHERE name = ? AND file LIKE ?", (name, f"%{path}")).fetchall()
    for f, start, end in rows:
        print(f"{f}:{start}-{end}")
        lines = (ROOT / f).read_text().splitlines()[start - 1 : end]
        for n, text in enumerate(lines[:SHOW_LIMIT], start):
            print(f"{n:>5}  {text}")
        if len(lines) > SHOW_LIMIT:
            print(f"... {len(lines) - SHOW_LIMIT} more lines")


def cmd_callers(db, name):
    rows = db.execute("SELECT file, line, kind, symbol FROM refs WHERE name = ? ORDER BY file, line", (name,))
    out([f"{f}:{line}  {kind}  in {symbol}" for f, line, kind, symbol in rows])


def cmd_callees(db, symbol):
    rows = db.execute("SELECT file, line, kind, name FROM refs WHERE symbol = ? ORDER BY file, line", (symbol,))
    out([f"{f}:{line}  {kind}  {name}" for f, line, kind, name in rows])


def relation(table):
    columns = [c.strip() for c in TABLES[table].split(",")]

    def run(db, pattern=""):
        where = " OR ".join(f"{c} LIKE ?" for c in columns)
        rows = db.execute(f"SELECT * FROM {table} WHERE {where} ORDER BY file, line", [f"%{pattern}%"] * len(columns))
        out([f"{f}:{line}  " + "  ".join(str(v) for v in rest) for f, line, *rest in rows])

    return run


def cmd_endpoint(db, pattern=""):
    eps = db.execute("SELECT file, line, method, path, symbol FROM endpoints ORDER BY path").fetchall()

    def owner(url):
        hits = [e for e in eps if re.fullmatch("[^/]+".join(map(re.escape, re.sub(r"\{[^}]*\}", "{}", e[3]).split("{}"))), url)]
        return min(hits, key=lambda e: e[3].count("{"), default=None)

    detail = {e: [] for e in eps}
    for f, line, url, symbol in db.execute("SELECT file, line, url, symbol FROM api_urls ORDER BY file, line"):
        if ep := owner(url):
            detail[ep].append(f"  url   {f}:{line}  {symbol}")
            for cf, cl, csym in db.execute("SELECT file, line, symbol FROM refs WHERE name = ? ORDER BY file, line", (symbol,)):
                detail[ep].append(f"        used  {cf}:{cl}  {csym}")
    for f, line, symbol, url in db.execute("SELECT file, line, symbol, url FROM tests_hit ORDER BY file, line"):
        if ep := owner(url):
            detail[ep].append(f"  test  {f}:{line}  {symbol}")
    lines = []
    for ep in eps:
        file, line, method, path, symbol = ep
        if pattern not in path and pattern not in symbol:
            continue
        lines.append(f"{method} {path}  {file}:{line}  {symbol}")
        sql = db.execute("SELECT DISTINCT table_name, mode FROM sql_refs WHERE file = ? AND symbol = ?", (file, symbol))
        lines += [f"  sql   {table} ({mode})" for table, mode in sql]
        lines += detail[ep]
    out(lines)


COMMANDS = {
    "find": (cmd_find, "PATTERN", "symbols whose name contains PATTERN"),
    "outline": (cmd_outline, "FILE", "symbols of a file, with start-end lines"),
    "show": (cmd_show, "NAME [FILE]", "source of a symbol"),
    "callers": (cmd_callers, "NAME", "where NAME is called, rendered or referenced"),
    "callees": (cmd_callees, "SYMBOL", "what SYMBOL calls, renders or references"),
    "endpoint": (cmd_endpoint, "[PATH]", "endpoint with its frontend users, tests and SQL"),
    **{t: (relation(t), "[FILTER]", f"rows of the {t} relation") for t in TABLES if t not in ("symbols", "refs")},
}


def main(argv):
    if argv[:1] == ["build"]:
        return build()
    if not argv or argv[0] not in COMMANDS:
        print("usage: codegraph.py build | <command> [args]")
        for name, (_, args, doc) in COMMANDS.items():
            print(f"  {name:<10} {args:<12} {doc}")
        return
    if not DB_PATH.exists():
        sys.exit("No graph yet. Run: tools/codegraph.py build")
    with sqlite3.connect(DB_PATH) as db:
        COMMANDS[argv[0]][0](db, *argv[1:])


if __name__ == "__main__":
    main(sys.argv[1:])
