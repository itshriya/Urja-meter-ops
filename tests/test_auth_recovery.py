from unittest.mock import AsyncMock

import pytest
import httpx

from app.integrations.urja.auth import ensure_portal_session


@pytest.mark.asyncio
async def test_expired_session_triggers_login():
    client = AsyncMock(spec=httpx.AsyncClient)

    with (
        pytest.MonkeyPatch.context() as monkeypatch,
    ):
        monkeypatch.setattr(
            "app.integrations.urja.auth.verify_portal_session",
            AsyncMock(side_effect=[False, True]),
        )
        login_mock = AsyncMock(return_value=True)
        monkeypatch.setattr(
            "app.integrations.urja.auth.login_to_portal",
            login_mock,
        )

        await ensure_portal_session(client)

    login_mock.assert_awaited_once_with(client)


@pytest.mark.asyncio
async def test_session_recovery_fails_if_login_does_not_restore_session():
    client = AsyncMock(spec=httpx.AsyncClient)

    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(
            "app.integrations.urja.auth.verify_portal_session",
            AsyncMock(return_value=False),
        )
        monkeypatch.setattr(
            "app.integrations.urja.auth.login_to_portal",
            AsyncMock(return_value=True),
        )

        with pytest.raises(
            RuntimeError,
            match="Unable to establish a valid portal session",
        ):
            await ensure_portal_session(client)
