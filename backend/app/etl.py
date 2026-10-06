import csv
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

from .db import DB_PATH

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
CSV_2017 = DATA_DIR / "Global-Coal-Plant-Tracker-Jan-2017.csv"
CSV_2023 = DATA_DIR / "Global-Coal-Plant-Tracker-July-2023.csv"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def parse_mw(value: str) -> float | None:
    try:
        return float(value.replace(",", ""))
    except ValueError:
        return None


def operating_by_country(rows: list[dict[str, str]]) -> dict[str, float]:
    totals: dict[str, float] = defaultdict(float)
    for row in rows:
        mw = parse_mw(row["Capacity (MW)"])
        if mw is not None and row["Status"].lower() == "operating":
            totals[row["Country"]] += mw
    return totals


def build(csv_2017: Path, csv_2023: Path, db_path: Path) -> None:
    mw_2017 = operating_by_country(read_rows(csv_2017))
    mw_2023 = operating_by_country(read_rows(csv_2023))
    db_path.unlink(missing_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE country_capacity (name TEXT PRIMARY KEY, mw_2017 REAL, mw_2023 REAL)")
        conn.executemany(
            "INSERT INTO country_capacity VALUES (?, ?, ?)",
            [(name, mw_2017.get(name, 0.0), mw_2023.get(name, 0.0)) for name in mw_2017.keys() | mw_2023.keys()],
        )


if __name__ == "__main__":
    build(CSV_2017, CSV_2023, DB_PATH)
    print(f"Wrote {DB_PATH}", file=sys.stderr)
