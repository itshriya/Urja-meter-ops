import httpx
import pytest

from app.integrations.urja.auth import (
    ensure_portal_session,
    verify_portal_session,
)


@pytest.mark.asyncio
async def test_verify_portal_session_returns_true_when_portal_responds():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"data": [], "total": 0})

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler)
    ) as client:
        # This test uses the configured portal URL, so replace the
        # request handler rather than making a real network request.
        result = await verify_portal_session(client)

    assert result is True
