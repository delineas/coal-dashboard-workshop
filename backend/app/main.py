import csv
import io

from fastapi import FastAPI, HTTPException, Response

from . import db

app = FastAPI(title="Coal Dashboard", version="0.1.0")

COUNTRY_SQL = "SELECT * FROM country_capacity WHERE (mw_2017 > 0 OR mw_2023 > 0)"
COUNTRY_PLANTS_SQL = """
SELECT id, name, subnational_unit, mw17, mw23, cmp17, cmp23, change
FROM plant_capacity
WHERE country = ? AND change IS NOT NULL
ORDER BY mw23 DESC, mw17 DESC
"""


@app.get("/api/countries")
def countries():
    return db.query_all(f"{COUNTRY_SQL} ORDER BY mw_2023 DESC")


CSV_COLUMNS = {
    "name": "Country",
    "mw_2017": "MW 2017",
    "mw_2023": "MW 2023",
    "delta_mw": "Δ MW",
    "pct_change": "Δ %",
    "coverage_mw": "Coverage",
    "trend": "Trend",
}


@app.get("/api/countries.csv")
def countries_csv():
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(CSV_COLUMNS.values())
    # shortcut: rows keep the API order (MW 2023, largest first), not the sort the user picked in the table; pass the sort key as a query parameter when an analyst asks for it.
    for row in countries():
        # shortcut: raw numbers and an empty Δ % for "new" or "not comparable", not the labels of the table; add a label column if analysts misread the empty cells.
        writer.writerow(row[key] for key in CSV_COLUMNS)
    # shortcut: the full file is built in memory, which is fine for 82 countries; stream the response if the export grows to plant or unit rows.
    # shortcut: fixed file name with no date, so weekly downloads overwrite each other.
    return Response(
        out.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="countries.csv"'},
    )


@app.get("/api/countries/{name}")
def country(name: str):
    row = db.query_one(f"{COUNTRY_SQL} AND name = ?", (name,))
    if not row:
        raise HTTPException(status_code=404, detail="Country not found")
    return {**row, "plants": db.query_all(COUNTRY_PLANTS_SQL, (name,))}


MAP_SQL = (
    "SELECT id, name, lat, lon, mw17, mw23, cmp17, cmp23, change FROM plant_capacity"
    " WHERE change IS NOT NULL AND lat IS NOT NULL AND lon IS NOT NULL"
)


@app.get("/api/plants/map")
def plant_map(country: str | None = None):
    if country is None:
        return db.query_all(MAP_SQL)
    return db.query_all(f"{MAP_SQL} AND country = ?", (country,))


PLANT_UNITS_SQL = """
SELECT
    tracker_id, name, COALESCE(mw_2023, mw_2017) AS mw, status_2017, status_2023,
    start_year, retired_year, technology, comparable
FROM units
WHERE plant_id = ?
ORDER BY name
"""


@app.get("/api/plants/{plant_id}")
def plant(plant_id: str):
    row = db.query_one("SELECT * FROM plant_capacity WHERE id = ?", (plant_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Plant not found")
    units = [{**unit, "comparable": bool(unit["comparable"])} for unit in db.query_all(PLANT_UNITS_SQL, (plant_id,))]
    return {**row, "units": units}
