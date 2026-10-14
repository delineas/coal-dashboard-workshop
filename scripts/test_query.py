import sqlite3

import pytest

from query import run


@pytest.fixture
def db(tmp_path):
    path = tmp_path / "coal.sqlite"
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE units (country TEXT, mw REAL)")
        conn.execute("INSERT INTO units VALUES ('Vietnam', 600)")
    return path


def test_run_returns_the_header_and_the_rows(db):
    assert run("SELECT country, mw FROM units", db) == [("country", "mw"), ("Vietnam", 600.0)]


def test_run_cannot_change_the_data(db):
    with pytest.raises(sqlite3.OperationalError, match="readonly"):
        run("DELETE FROM units", db)
