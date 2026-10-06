from fastapi import FastAPI

from . import db

app = FastAPI(title="Basecamp Tool", version="0.1.0")


@app.get("/api/hello")
def hello():
    return {"message": "Hello world", "sqlite": db.query_one("SELECT sqlite_version() AS v")["v"]}
