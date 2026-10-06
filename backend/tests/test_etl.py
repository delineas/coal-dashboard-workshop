import sqlite3
from pathlib import Path

import pytest

from app import etl

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def conn(tmp_path):
    db_path = tmp_path / "coal.sqlite"
    etl.build(FIXTURES / "units_2017.csv", FIXTURES / "units_2023.csv", db_path)
    with sqlite3.connect(db_path) as connection:
        yield connection


def test_operating_capacity_by_country(conn):
    rows = {name: (mw17, mw23) for name, mw17, mw23 in conn.execute("SELECT * FROM country_capacity")}
    assert rows == {"Atlantis": (100, 100), "Lemuria": (1200, 0), "Mu": (0, 300), "Türkiye": (80, 80)}


def test_2017_country_names_use_2023_names(conn):
    names = {name for (name,) in conn.execute("SELECT name FROM country_capacity")}
    assert "Türkiye" in names
    assert "Turkey" not in names


def test_unknown_2017_country_stops_the_etl(tmp_path):
    with pytest.raises(etl.UnknownCountryError, match="Hyperborea"):
        etl.build(FIXTURES / "units_2017_unknown_country.csv", FIXTURES / "units_2023.csv", tmp_path / "coal.sqlite")
