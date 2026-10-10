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
    return {row[0]: row[1:] for row in conn.execute("SELECT name, mw_2017, mw_2023 FROM country_capacity")}


def test_operating_capacity_by_country(conn):
    assert country_rows(conn) == {
        "Atlantis": (540, 300),
        "Lemuria": (1200, 0),
        "Mu": (70, 395),
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


def comparable(conn, tracker_id):
    return conn.execute("SELECT comparable FROM units WHERE tracker_id = ?", (tracker_id,)).fetchone()[0]


def test_unit_in_both_files_is_comparable(conn):
    assert comparable(conn, "G1") == 1


def test_2023_unit_that_started_in_2017_or_later_is_comparable(conn):
    assert comparable(conn, "G4") == 1


def test_2023_unit_that_started_before_2017_is_not_comparable(conn):
    assert comparable(conn, "G8") == 0


def test_2017_only_unit_is_not_comparable(db_path):
    etl.build(FIXTURES / "units_2017.csv", FIXTURES / "units_2023_without_g6.csv", db_path)
    with sqlite3.connect(db_path) as connection:
        assert comparable(connection, "G6") == 0


def test_country_change_uses_comparable_units(conn):
    mu = conn.execute(
        "SELECT mw_2017, mw_2023, cmp_2017, cmp_2023, delta_mw, coverage_mw, trend FROM country_capacity WHERE name = 'Mu'"
    ).fetchone()
    assert mu == (70, 395, 70, 370, 300, 25, "up")


def test_pct_change_uses_comparable_2017_capacity(conn):
    assert conn.execute("SELECT pct_change FROM country_capacity WHERE name = 'Mu'").fetchone()[0] == pytest.approx(428.57, 0.01)


def plant_of(conn, tracker_id):
    return conn.execute("SELECT plant_id FROM units WHERE tracker_id = ?", (tracker_id,)).fetchone()[0]


def test_2023_unit_belongs_to_its_location(conn):
    assert plant_of(conn, "G4") == "L3"


def test_2017_only_unit_joins_the_plant_of_a_sibling_unit(conn):
    assert plant_of(conn, "G11") == "L7"


def test_2017_only_unit_without_sibling_gets_a_stable_synthetic_plant(tmp_path):
    plant_ids = []
    for name in ("first.sqlite", "second.sqlite"):
        etl.build(FIXTURES / "units_2017.csv", FIXTURES / "units_2023.csv", tmp_path / name)
        with sqlite3.connect(tmp_path / name) as connection:
            plant_ids.append(plant_of(connection, "G12"))
    assert plant_ids[0].startswith("L17-")
    assert plant_ids[0] == plant_ids[1]


def test_plant_record_and_capacity(conn):
    kappa = conn.execute("SELECT name, country, owner, lat, mw17, mw23, cmp17, cmp23 FROM plant_capacity WHERE id = 'L7'").fetchone()
    assert kappa == ("Kappa", "Atlantis", "Owner K", 11, 350, 200, 200, 200)


@pytest.mark.parametrize(
    ("plant_id", "change"),
    [("L3", "new"), ("L2", "retired"), ("L1", "unchanged"), ("L6", "coverage"), ("L5", "unchanged")],
)
def test_plant_change(conn, plant_id, change):
    assert conn.execute("SELECT change FROM plant_capacity WHERE id = ?", (plant_id,)).fetchone()[0] == change


def test_plant_change_grew_and_shrank(tmp_path):
    db_path = tmp_path / "coal.sqlite"
    etl.build(FIXTURES / "units_2017_resized.csv", FIXTURES / "units_2023.csv", db_path)
    with sqlite3.connect(db_path) as connection:
        changes = dict(connection.execute("SELECT id, change FROM plant_capacity WHERE id IN ('L1', 'L7')"))
    assert changes == {"L1": "grew", "L7": "shrank"}
