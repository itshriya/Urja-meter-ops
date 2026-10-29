
import httpx

from app.core.config import get_settings


async def get_meter_geo(
    client: httpx.AsyncClient,
    meter_id: str,
) -> dict:
    settings = get_settings()

    url = (
        f"{settings.portal_base_url.rstrip('/')}"
        f"/portal/meters/{meter_id}/geo"
    )

    response = await client.get(url)
    response.raise_for_status()

    return response.json()


async def get_meter_energy(
    client: httpx.AsyncClient,
    meter_id: str,
) -> dict:
    settings = get_settings()

    url = (
        f"{settings.portal_base_url.rstrip('/')}"
        f"/portal/meters/{meter_id}/energy"
    )

    response = await client.get(url)
    response.raise_for_status()

    return response.json()
