import csv
import sqlite3
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from .db import DB_PATH

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
CSV_2017 = DATA_DIR / "Global-Coal-Plant-Tracker-Jan-2017.csv"
CSV_2023 = DATA_DIR / "Global-Coal-Plant-Tracker-July-2023.csv"

COUNTRY_NAMES_2017 = {
    "Turkey": "Türkiye",
    "FYROM": "North Macedonia",
    "Swaziland": "Eswatini",
    "Democratic Republic of Congo": "DR Congo",
    "Bosnia & Herzegovina": "Bosnia and Herzegovina",
}
COUNTRIES_ONLY_2017 = {"Jordan", "Reunion"}

SCHEMA = """
CREATE TABLE units (
    tracker_id TEXT PRIMARY KEY,
    country TEXT NOT NULL,
    status_2017 TEXT,
    mw_2017 REAL,
    status_2023 TEXT,
    mw_2023 REAL
);
CREATE VIEW country_capacity AS
SELECT
    country AS name,
    SUM(CASE WHEN status_2017 = 'operating' THEN mw_2017 ELSE 0 END) AS mw_2017,
    SUM(CASE WHEN status_2023 = 'operating' THEN mw_2023 ELSE 0 END) AS mw_2023
FROM units
GROUP BY country;
"""


class UnknownCountryError(ValueError):
    pass


@dataclass
class Unit:
    tracker_id: str
    country: str
    status_2017: str | None = None
    mw_2017: float | None = None
    status_2023: str | None = None
    mw_2023: float | None = None


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def parse_mw(value: str) -> float | None:
    try:
        return float(value.replace(",", ""))
    except ValueError:
        return None


def clean_2017(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], Counter[str]]:
    kept, seen, discarded = [], set(), Counter()
    for row in rows:
        if not row["Status"] or parse_mw(row["Capacity (MW)"]) is None:
            discarded["empty status or capacity"] += 1
        elif not row["Tracker ID"]:
            discarded["empty Tracker ID"] += 1
        elif row["Tracker ID"] in seen:
            discarded["duplicate Tracker ID"] += 1
        else:
            seen.add(row["Tracker ID"])
            kept.append(row)
    return kept, discarded


def normalize_2017_countries(rows_2017: list[dict[str, str]], rows_2023: list[dict[str, str]]) -> None:
    known = {row["Country"] for row in rows_2023} | COUNTRIES_ONLY_2017
    for row in rows_2017:
        row["Country"] = COUNTRY_NAMES_2017.get(row["Country"], row["Country"])
        if row["Country"] not in known:
            raise UnknownCountryError(f"Unknown 2017 country: {row['Country']}")


def merge_units(rows_2017: list[dict[str, str]], rows_2023: list[dict[str, str]]) -> dict[str, Unit]:
    units = {
        row["Tracker ID"]: Unit(
            row["Tracker ID"], row["Country"], row["Status"].lower(), parse_mw(row["Capacity (MW)"])
        )
        for row in rows_2017
    }
    for row in rows_2023:
        unit = units.setdefault(row["Tracker ID"], Unit(row["Tracker ID"], row["Country"]))
        unit.country = row["Country"]
        unit.status_2023 = row["Status"].lower()
        unit.mw_2023 = parse_mw(row["Capacity (MW)"])
    return units


def build(csv_2017: Path, csv_2023: Path, db_path: Path) -> Counter[str]:
    rows_2017, discarded = clean_2017(read_rows(csv_2017))
    rows_2023 = read_rows(csv_2023)
    normalize_2017_countries(rows_2017, rows_2023)
    units = merge_units(rows_2017, rows_2023)
    db_path.unlink(missing_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.executescript(SCHEMA)
        conn.executemany(
            "INSERT INTO units VALUES (?, ?, ?, ?, ?, ?)",
            [(u.tracker_id, u.country, u.status_2017, u.mw_2017, u.status_2023, u.mw_2023) for u in units.values()],
        )
    return discarded


if __name__ == "__main__":
    discarded = build(CSV_2017, CSV_2023, DB_PATH)
    for reason, count in discarded.items():
        print(f"Discarded 2017 rows ({reason}): {count}", file=sys.stderr)
    print(f"Wrote {DB_PATH}", file=sys.stderr)
