from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app


def test_meter_geo_rejects_invalid_meter_id():
    api_key = get_settings().api_key.get_secret_value()

    with patch("app.routes.meters.get_meter_geo") as mock_get_geo:
        with TestClient(app) as client:
            response = client.get(
                "/meters/J100%20000/geo",
                headers={"X-API-Key": api_key},
            )

    assert response.status_code == 422
    mock_get_geo.assert_not_called()


def test_meter_energy_rejects_invalid_meter_id():
    api_key = get_settings().api_key.get_secret_value()

    with patch("app.routes.meters.get_meter_energy") as mock_get_energy:
        with TestClient(app) as client:
            response = client.get(
                "/meters/J100%20000/energy",
                headers={"X-API-Key": api_key},
            )

    assert response.status_code == 422
    mock_get_energy.assert_not_called()
