import asyncio

from app.core.config import get_settings
from app.core.http_client import create_http_client
from app.integrations.urja.auth import login_to_portal
from app.integrations.urja.meters import search_meters


async def main():
    settings = get_settings()

    client = create_http_client(
        settings.portal_timeout_seconds
    )

    try:
        await login_to_portal(client)

        result = await search_meters(
            client,
            query="J100000",
            page=1,
        )

        print("Response keys:", list(result.keys()))

        meters = result.get("data", [])
        print("Meters returned:", len(meters))

        if meters:
            print("First meter:", meters[0])

    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(main())