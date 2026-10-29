import httpx

from app.core.config import get_settings


async def login_to_portal(client: httpx.AsyncClient) -> bool:
    settings = get_settings()
    base_url = settings.portal_base_url.rstrip("/")
    login_url = f"{base_url}/login"

    # Establish the initial session and obtain any required cookies.
    initial_response = await client.get(login_url)
    initial_response.raise_for_status()

    form_data = {
        "email": settings.portal_username,
        "password": settings.portal_password.get_secret_value(),
    }

    response = await client.post(
        login_url,
        data=form_data,
        headers={
            "Origin": base_url,
            "Referer": login_url,
        },
    )
    response.raise_for_status()

    try:
        result = response.json()
    except ValueError as error:
        raise RuntimeError(
            "Portal returned an unexpected login response"
        ) from error

    if (
        result.get("type") != "redirect"
        or result.get("location") != "/meters"
    ):
        raise RuntimeError("Portal login was not successful")

    return True


async def verify_portal_session(client: httpx.AsyncClient) -> bool:
    settings = get_settings()
    url = (
        f"{settings.portal_base_url.rstrip('/')}"
        "/portal/meters/search"
    )

    response = await client.get(
        url,
        params={"q": "J100000", "page": 1},
    )

    # A successful authenticated request indicates a usable session.
    if response.status_code in (401, 403):
        return False

    response.raise_for_status()
    return True


async def ensure_portal_session(client: httpx.AsyncClient) -> None:
    if await verify_portal_session(client):
        return

    await login_to_portal(client)

    if not await verify_portal_session(client):
        raise RuntimeError("Unable to establish a valid portal session")
