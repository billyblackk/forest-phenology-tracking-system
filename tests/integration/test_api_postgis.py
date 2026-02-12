import os
from datetime import date

import pytest
from fastapi.testclient import TestClient

from fpts.api.main import create_app
from fpts.config.settings import Settings
from fpts.domain.models import Location, PhenologyMetric


@pytest.mark.integration
def test_phenology_point_returns_seeded_metric_postgis():
    dsn = os.getenv("FPTS_TEST_DATABASE_DSN")
    if not dsn:
        pytest.skip(
            "SKIPPED: Set FPTS_TEST_DATABASE_DSN to run PostGIS integration tests"
        )

    app = create_app(
        settings=Settings(
            database_dsn=dsn,
        )
    )

    # Seed explicitly into PostGIS via the repo (same test shape as memory)
    repo = app.state.phenology_repo
    loc = Location(lat=52.5, lon=13.4)
    repo.add_metric(
        product="test_product",
        metric=PhenologyMetric(
            year=2020,
            location=loc,
            sos_date=date(2020, 4, 15),
            eos_date=date(2020, 10, 15),
            season_length=(date(2020, 10, 15) - date(2020, 4, 15)).days,
            is_forest=True,
        ),
    )

    client = TestClient(app)
    resp = client.get(
        "/phenology/point",
        params={"product": "test_product", "lat": 52.5, "lon": 13.4, "year": 2020},
    )
    assert resp.status_code == 200
