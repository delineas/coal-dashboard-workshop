from fastapi import FastAPI, HTTPException

from . import db

app = FastAPI(title="Coal Dashboard", version="0.1.0")

COUNTRY_SQL = "SELECT * FROM country_capacity WHERE (mw_2017 > 0 OR mw_2023 > 0)"
COUNTRY_PLANTS_SQL = """
SELECT id, name, subnational_unit, mw17, mw23, cmp17, cmp23
FROM plant_capacity
WHERE country = ? AND (mw17 > 0 OR mw23 > 0)
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
