# Property-based (fuzz) test: Hypothesis generates many random country names and checks one rule for all of them.
# It protects the country endpoint against unexpected input: an unknown name must always give 404, never 200 or 500.
# Known exception, excluded here: a name made only of "/" and "." (or an empty name) collapses into /api/countries/,
# and the API redirects to the country list (200). Hypothesis found the "/" case.
from urllib.parse import quote

from fastapi.testclient import TestClient
from hypothesis import given, settings
from hypothesis import strategies as st

from app.main import app

client = TestClient(app)
REAL_NAMES = {c["name"] for c in client.get("/api/countries").json()}


def is_unknown_name(name):
    return name not in REAL_NAMES and set(name) - {"/", "."}


@settings(max_examples=50, deadline=None)
@given(st.text(min_size=1).filter(is_unknown_name))
def test_unknown_country_returns_404(name):
    assert client.get("/api/countries/" + quote(name, safe="")).status_code == 404
