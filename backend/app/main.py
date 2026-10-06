from fastapi import FastAPI

from . import db

app = FastAPI(title="Coal Dashboard", version="0.1.0")


@app.get("/api/countries")
def countries():
    return db.query_all(
        "SELECT name, mw_2017, mw_2023 FROM country_capacity"
        " WHERE mw_2017 > 0 OR mw_2023 > 0 ORDER BY mw_2023 DESC"
    )
