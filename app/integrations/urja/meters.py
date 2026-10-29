
import httpx

from app.core.config import get_settings


async def search_meters(
    client: httpx.AsyncClient,
    query: str = "",
    page: int = 1,
) -> dict:
    settings = get_settings()

    url = (
        f"{settings.portal_base_url.rstrip('/')}"
        "/portal/meters/search"
    )

    response = await client.get(
        url,
        params={
            "q": query,
            "page": page,
        },
    )

    response.raise_for_status()

    return response.json()
