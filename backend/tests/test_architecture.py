# Architecture test: checks a structural rule of the code, not a behavior (ADR 0001).
# It protects the layers: the API reads only SQLite through app.db. It does not run the ETL, open SQLite or read files.
import ast
from pathlib import Path

MAIN = ast.parse((Path(__file__).parent.parent / "app" / "main.py").read_text())


def imported_modules(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            yield from (alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            yield node.module or ""
            yield from (alias.name for alias in node.names)


def test_api_does_not_import_the_etl_or_sqlite3():
    modules = set(imported_modules(MAIN))
    assert not modules & {"etl", "app.etl", "sqlite3"}


def test_api_does_not_open_files():
    calls = {node.func.id for node in ast.walk(MAIN) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
    assert "open" not in calls
