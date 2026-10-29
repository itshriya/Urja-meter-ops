
import asyncio

from app.core.config import get_settings
from app.core.http_client import create_http_client
from app.integrations.urja.auth import (
    login_to_portal,
    verify_portal_session,
)


async def main():
    settings = get_settings()

    client = create_http_client(
        settings.portal_timeout_seconds
    )

    try:
        await login_to_portal(client)

        valid = await verify_portal_session(client)

        print("Portal session valid:", valid)

    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
