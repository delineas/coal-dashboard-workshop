from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


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
    countries = {c["name"]: c for c in client.get("/api/countries").json()}
    assert (countries["Hong Kong"]["mw_2017"], countries["Hong Kong"]["mw_2023"]) == (6_608, 6_112)
    assert countries["China"]["mw_2017"] == 914_619
