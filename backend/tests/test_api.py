from fastapi.testclient import TestClient

from app import db
from app.main import app

client = TestClient(app)


def unit(tracker_id):
    return db.query_one("SELECT country, op_2017, op_2023, comparable FROM units WHERE tracker_id = ?", (tracker_id,))


def test_countries_global_totals():
    countries = client.get("/api/countries").json()
    assert sum(c["mw_2017"] for c in countries) == 1_965_448
    assert sum(c["mw_2023"] for c in countries) == 2_095_083


def test_countries_sorted_and_without_zero_rows():
    countries = client.get("/api/countries").json()
    assert [c["mw_2023"] for c in countries] == sorted((c["mw_2023"] for c in countries), reverse=True)
    assert all(c["mw_2017"] > 0 or c["mw_2023"] > 0 for c in countries)


def test_countries_count():
    assert len(client.get("/api/countries").json()) == 82


def test_units_count_for_their_2023_country_in_both_years():
    countries = countries_by_name()
    assert (countries["Hong Kong"]["mw_2017"], countries["Hong Kong"]["mw_2023"]) == (6_608, 6_112)
    assert countries["China"]["mw_2017"] == 914_619


def countries_by_name():
    return {c["name"]: c for c in client.get("/api/countries").json()}


def test_country_fields():
    fields = {"name", "mw_2017", "mw_2023", "cmp_2017", "cmp_2023", "delta_mw", "coverage_mw", "pct_change", "trend"}
    assert all(set(c) == fields for c in client.get("/api/countries").json())


def test_global_comparable_change():
    countries = client.get("/api/countries").json()
    assert sum(c["cmp_2017"] for c in countries) == 1_921_722
    assert sum(c["cmp_2023"] for c in countries) == 2_054_880
    assert sum(c["delta_mw"] for c in countries) == 133_158
    assert sum(c["coverage_mw"] for c in countries) == -3_523


def test_unit_added_to_the_tracker_later_is_only_in_the_snapshot():
    assert unit("G113594") == {"country": "Czech Republic", "op_2017": 0, "op_2023": 30, "comparable": 0}


def test_unit_built_after_2017_is_comparable():
    assert unit("G114937") == {"country": "China", "op_2017": 0, "op_2023": 50, "comparable": 1}


def test_unit_removed_from_the_tracker_is_not_comparable():
    assert unit("G110459") == {"country": "South Korea", "op_2017": 50, "op_2023": 0, "comparable": 0}


def test_pct_change_is_null_without_comparable_2017_capacity():
    assert countries_by_name()["Panama"]["pct_change"] is None


def test_country_detail():
    response = client.get("/api/countries/Türkiye")
    assert response.status_code == 200
    detail = response.json()
    assert {k: v for k, v in detail.items() if k != "plants"} == countries_by_name()["Türkiye"]


def test_country_plants_add_up_to_the_country_totals():
    india = client.get("/api/countries/India").json()
    assert sum(p["mw17"] for p in india["plants"]) == india["mw_2017"]
    assert sum(p["mw23"] for p in india["plants"]) == india["mw_2023"]
    assert sum(p["cmp23"] - p["cmp17"] for p in india["plants"]) == india["delta_mw"]
    assert all(p["mw17"] > 0 or p["mw23"] > 0 for p in india["plants"])


def test_unknown_country_returns_404():
    assert client.get("/api/countries/Atlantis").status_code == 404


def test_country_plants_have_a_change():
    india = client.get("/api/countries/India").json()
    assert all(p["change"] in {"new", "retired", "grew", "shrank", "unchanged", "coverage"} for p in india["plants"])


def test_plant_with_coverage_change_only():
    kazakhstan = client.get("/api/countries/Kazakhstan").json()
    stepnogorsk = next(p for p in kazakhstan["plants"] if p["id"] == "L104985")
    assert stepnogorsk["change"] == "coverage"


def test_plant_detail():
    plant = client.get("/api/plants/L104985").json()
    assert (plant["name"], plant["country"], plant["change"]) == ("Stepnogorsk power station", "Kazakhstan", "coverage")
    assert {"owner", "parent", "subnational_unit", "lat", "lon", "wiki_url", "mw17", "mw23"} <= plant.keys()
    assert plant["units"]
    assert all(unit["comparable"] is False for unit in plant["units"])


def test_unknown_plant_returns_404():
    assert client.get("/api/plants/L000000").status_code == 404


def test_plant_without_operating_capacity_still_returns_its_units():
    plant = client.get("/api/plants/L100001").json()
    assert (plant["mw17"], plant["mw23"], plant["change"]) == (0, 0, None)
    assert plant["units"]


def test_map_plants_have_coordinates_and_a_change():
    plants = client.get("/api/plants/map").json()
    assert all(p["lat"] is not None and p["lon"] is not None and p["change"] is not None for p in plants)


def test_plant_without_coordinates_is_not_on_the_map():
    without_coordinates = db.query_one(
        "SELECT id FROM plant_capacity WHERE change IS NOT NULL AND lat IS NULL ORDER BY id LIMIT 1"
    )["id"]
    assert without_coordinates not in {p["id"] for p in client.get("/api/plants/map").json()}


def test_map_country_filter():
    india = client.get("/api/plants/map", params={"country": "India"}).json()
    india_ids = {p["id"] for p in client.get("/api/countries/India").json()["plants"]}
    assert india
    assert {p["id"] for p in india} <= india_ids
    assert all(p["lat"] is not None and p["change"] is not None for p in india)
