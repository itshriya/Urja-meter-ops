
import httpx

from app.core.config import get_settings


async def get_transformers(
    client: httpx.AsyncClient,
    page: int = 1,
) -> dict:
    settings = get_settings()

    url = (
        f"{settings.portal_base_url.rstrip('/')}"
        "/portal/dts"
    )

    response = await client.get(
        url,
        params={"page": page},
    )
    response.raise_for_status()

    return response.json()
