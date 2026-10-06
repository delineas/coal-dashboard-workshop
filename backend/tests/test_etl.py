import sqlite3
from pathlib import Path

import pytest

from app import etl

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "coal.sqlite"


@pytest.fixture
def conn(db_path):
    etl.build(FIXTURES / "units_2017.csv", FIXTURES / "units_2023.csv", db_path)
    with sqlite3.connect(db_path) as connection:
        yield connection


def country_rows(conn):
    return {name: (mw17, mw23) for name, mw17, mw23 in conn.execute("SELECT * FROM country_capacity")}


def test_operating_capacity_by_country(conn):
    assert country_rows(conn) == {
        "Atlantis": (100, 100),
        "Lemuria": (1200, 0),
        "Mu": (70, 370),
        "Türkiye": (80, 80),
    }


def test_2017_country_names_use_2023_names(conn):
    assert "Turkey" not in country_rows(conn)


def test_unknown_2017_country_stops_the_etl(db_path):
    with pytest.raises(etl.UnknownCountryError, match="Hyperborea"):
        etl.build(FIXTURES / "units_2017_unknown_country.csv", FIXTURES / "units_2023.csv", db_path)


def test_bad_2017_rows_are_discarded(db_path):
    discarded = etl.build(FIXTURES / "units_2017.csv", FIXTURES / "units_2023.csv", db_path)
    assert discarded == {"empty status or capacity": 2, "empty Tracker ID": 1, "duplicate Tracker ID": 1}


def test_first_duplicate_row_is_kept(conn):
    assert conn.execute("SELECT status_2017, mw_2017 FROM units WHERE tracker_id = 'G3'").fetchone() == ("operating", 1200)


def test_unit_uses_its_2023_country_for_both_years(conn):
    assert conn.execute("SELECT country FROM units WHERE tracker_id = 'G6'").fetchone() == ("Mu",)
