
import asyncio

from app.core.config import get_settings
from app.core.http_client import create_http_client
from app.integrations.urja.auth import login_to_portal


async def main():
    settings = get_settings()

    client = create_http_client(
        settings.portal_timeout_seconds
    )

    try:
        success = await login_to_portal(client)
        print("Login response received:", success)
        print("Session cookies stored:", len(client.cookies))
    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
