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
