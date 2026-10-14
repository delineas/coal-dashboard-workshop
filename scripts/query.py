"""Answer a question about the coal data with SQL, read-only.

Usage, from the repository root:
    python3 scripts/query.py "SELECT ..."   tab-separated rows, with a header
    python3 scripts/query.py                the schema of every table and view
"""
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "backend" / "coal.sqlite"
SCHEMA_SQL = "SELECT sql FROM sqlite_master WHERE sql IS NOT NULL"


def run(sql: str, db_path: Path = DB_PATH) -> list[tuple]:
    if not db_path.exists():
        sys.exit(f"{db_path} is missing. Build it first: cd backend && python3 -m app.etl")
    with sqlite3.connect(f"file:{db_path}?mode=ro", uri=True) as conn:
        cursor = conn.execute(sql)
        header = tuple(col[0] for col in cursor.description)
        return [header, *cursor.fetchall()]


def main(argv: list[str]) -> None:
    for row in run(argv[0] if argv else SCHEMA_SQL):
        print("\t".join("" if value is None else str(value) for value in row))


if __name__ == "__main__":
    main(sys.argv[1:])
