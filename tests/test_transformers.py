
import httpx
import pytest

from app.integrations.urja.transformers import get_transformers


@pytest.mark.asyncio
async def test_get_transformers_returns_data():
    mock_response = {
        "data": [
            {
                "code": "DT-001",
                "name": "Malviya Nagar DT 1",
                "feederCode": "F-001",
                "capacityKva": 100,
            }
        ]
    }

    def mock_handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/portal/dts"
        assert request.url.params["page"] == "1"

        return httpx.Response(
            status_code=200,
            json=mock_response,
        )

    transport = httpx.MockTransport(mock_handler)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="https://urja-ops.flockenergy.tech",
    ) as client:
        # The function reads the configured portal URL.
        # Patch settings to match this mock client.
        from unittest.mock import patch

        with patch(
            "app.integrations.urja.transformers.get_settings"
        ) as mock_settings:
            mock_settings.return_value.portal_base_url = (
                "https://urja-ops.flockenergy.tech"
            )

            result = await get_transformers(client, page=1)

    assert len(result["data"]) == 1
    assert result["data"][0]["code"] == "DT-001"
    assert result["data"][0]["capacityKva"] == 100
