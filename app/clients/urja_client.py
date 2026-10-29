from typing import Any

import httpx


async def get_json(
    client: httpx.AsyncClient,
    path: str,
    params: dict[str, str | int] | None = None,
) -> Any:
    """Fetch JSON data from the Urja portal."""

    try:
        response = await client.get(path, params=params)
        response.raise_for_status()
        return response.json()

    except httpx.TimeoutException as exc:
        raise RuntimeError("Urja portal request timed out") from exc

    except httpx.HTTPStatusError as exc:
        raise RuntimeError(
            f"Urja portal returned HTTP {exc.response.status_code}"
        ) from exc

    except httpx.RequestError as exc:
        raise RuntimeError("Could not connect to Urja portal") from exc

    except ValueError as exc:
        raise RuntimeError(
            "Urja portal returned invalid JSON"
        ) from exc


async def search_meters(
    client: httpx.AsyncClient,
    query: str = "",
    page: int = 1,
):
    return await get_json(
        client,
        "/portal/search",
        params={"q": query, "page": page},
    )


async def list_transformers(
    client: httpx.AsyncClient,
    page: int = 1,
):
    return await get_json(
        client,
        "/portal/dts",
        params={"page": page},
    )
