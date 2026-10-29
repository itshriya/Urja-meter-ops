from contextlib import asynccontextmanager

from app.core.http_client import create_http_client


@asynccontextmanager
async def lifespan(app):
    app.state.portal_client = create_http_client()

    try:
        yield
    finally:
        await app.state.portal_client.aclose()