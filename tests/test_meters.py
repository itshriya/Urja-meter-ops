from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app


def test_meter_search_route():
    settings = get_settings()
    valid_api_key = settings.api_key.get_secret_value()

    async def fake_ensure_session(client):
        return None

    async def fake_search_meters(client, query="", page=1):
        return {
            "data": [
                {
                    "meterId": "J100000",
                    "serialNo": "SE33962",
                    "make": "HPL",
                    "phaseType": "single",
                    "installStatus": "Decommissioned",
                    "dtCode": "DT-001",
                }
            ],
            "total": 1,
            "page": page,
            "pageSize": 20,
        }

    with patch(
        "app.routes.meters.ensure_portal_session",
        new=fake_ensure_session,
    ), patch(
        "app.routes.meters.search_meters",
        new=fake_search_meters,
    ):
        with TestClient(app) as client:
            response = client.get(
                "/meters/search",
                params={"q": "J100000", "page": 1},
                headers={"X-API-Key": valid_api_key},
            )

    assert response.status_code == 200
    assert response.json()["data"][0]["meterId"] == "J100000"
    assert response.json()["total"] == 1
