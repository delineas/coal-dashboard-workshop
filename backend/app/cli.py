import argparse
import sqlite3
import sys
from pathlib import Path

from .db import DB_PATH


def connect(db_path: Path) -> sqlite3.Connection:
    return sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)


def schema(conn: sqlite3.Connection) -> list[str]:
    names = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type IN ('table', 'view') ORDER BY rowid")]
    return [f"{name}({', '.join(col[1] for col in conn.execute(f'PRAGMA table_xinfo({name})'))})" for name in names]


def query(conn: sqlite3.Connection, sql: str, limit: int) -> list[str]:
    cursor = conn.execute(sql)
    lines = ["\t".join(col[0] for col in cursor.description)]
    lines += ["\t".join("" if value is None else str(value) for value in row) for row in cursor.fetchmany(limit)]
    if cursor.fetchone():
        lines.append(f"... more than {limit} rows")
    return lines


def main(argv: list[str] | None = None, db_path: Path = DB_PATH) -> None:
    parser = argparse.ArgumentParser(prog="coal", description="Query the coal database that the ETL builds from data/*.csv.")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("schema", help="list the tables and views with their columns")
    sql_parser = commands.add_parser("sql", help="run a read-only SQL query and print tab-separated rows")
    sql_parser.add_argument("query")
    sql_parser.add_argument("--limit", type=int, default=50)
    args = parser.parse_args(argv)

    with connect(db_path) as conn:
        try:
            lines = schema(conn) if args.command == "schema" else query(conn, args.query, args.limit)
        except sqlite3.Error as error:
            sys.exit(f"error: {error}")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
