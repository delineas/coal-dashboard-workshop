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
    assert rows == {"Atlantis": (100, 100), "Lemuria": (1200, 0), "Mu": (0, 300)}
