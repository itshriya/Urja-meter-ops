import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import get_settings
from app.core.http_client import create_http_client
from app.integrations.urja.auth import login_to_portal
from app.routes.meters import router as meters_router
from app.routes.transformers import router as transformers_router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    client = create_http_client(settings.portal_timeout_seconds)
    app.state.http_client = client
    app.state.portal_session_ready = False

    try:
        logger.info("Starting Flock Meter API")

        await login_to_portal(client)
        app.state.portal_session_ready = True

        logger.info("Portal login successful")
        yield

    except Exception:
        logger.exception("Application startup or runtime failure")
        raise

    finally:
        await client.aclose()
        logger.info("HTTP client closed")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Flock Meter API",
        version="1.0.0",
        description="API for accessing electricity meter information",
        lifespan=lifespan,
    )

    @app.get("/health")
    async def health_check():
        portal_ready = getattr(
            app.state,
            "portal_session_ready",
            False,
        )

        if not portal_ready:
            from fastapi.responses import JSONResponse

            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "portal_session": "not_ready",
                },
            )

        return {
            "status": "ok",
            "portal_session": "ready",
        }

    app.include_router(meters_router)
    app.include_router(transformers_router)

    return app


app = create_app()
