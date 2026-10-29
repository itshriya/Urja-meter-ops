
import httpx


def create_http_client(
    timeout_seconds: float,
) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        timeout=httpx.Timeout(timeout_seconds),
        follow_redirects=False,
        headers={
            "Accept": "application/json",
        },
    )
