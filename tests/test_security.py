from fastapi.testclient import TestClient

from app.main import app


def test_transformers_rejects_missing_api_key():
    with TestClient(app) as client:
        response = client.get("/transformers?page=1")

    assert response.status_code == 401


def test_transformers_rejects_invalid_api_key():
    with TestClient(app) as client:
        response = client.get(
            "/transformers?page=1",
            headers={"X-API-Key": "definitely-wrong"},
        )

    assert response.status_code == 401


def test_meter_search_rejects_missing_api_key():
    with TestClient(app) as client:
        response = client.get("/meters/search?q=J100000&page=1")

    assert response.status_code == 401


def test_meter_search_rejects_invalid_api_key():
    with TestClient(app) as client:
        response = client.get(
            "/meters/search?q=J100000&page=1",
            headers={"X-API-Key": "definitely-wrong"},
        )

    assert response.status_code == 401


def test_meter_geo_rejects_invalid_meter_id():
    with TestClient(app) as client:
        response = client.get(
            "/meters/J100%20000/geo",
            headers={"X-API-Key": "definitely-wrong"},
        )

    assert response.status_code == 401
