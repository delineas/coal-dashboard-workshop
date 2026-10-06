from fastapi import FastAPI, HTTPException

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


@app.get("/api/countries/{name}")
def country(name: str):
    row = db.query_one(f"{COUNTRY_SQL} AND name = ?", (name,))
    if not row:
        raise HTTPException(status_code=404, detail="Country not found")
    return {**row, "plants": db.query_all(COUNTRY_PLANTS_SQL, (name,))}


@app.get("/api/plants/map")
def plant_map():
    return db.query_all(
        "SELECT id, name, lat, lon, mw17, mw23, cmp17, cmp23, change FROM plant_capacity"
        " WHERE change IS NOT NULL AND lat IS NOT NULL AND lon IS NOT NULL"
    )


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
