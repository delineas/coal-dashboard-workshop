# Fitness test: checks a measurable quality goal (payload size), not a feature.
# It protects the map load time on slow networks (Refs #6). Today the payload is about 455 kB, so the test is an
# expected failure. strict=True makes it fail when the payload gets small: then remove the xfail mark to keep the guard.
import pytest
from fastapi.testclient import TestClient

from app.main import app

MAX_MAP_BYTES = 200_000


@pytest.mark.xfail(strict=True, reason="Refs #6: /api/plants/map is about 455 kB today")
def test_plant_map_payload_stays_under_200_kb():
    assert len(TestClient(app).get("/api/plants/map").content) < MAX_MAP_BYTES
