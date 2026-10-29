
import secrets

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

from app.core.config import get_settings


api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False,
)


async def verify_api_key(
    api_key: str | None = Security(api_key_header),
) -> None:
    settings = get_settings()
    expected_key = settings.api_key.get_secret_value()

    if not api_key or not secrets.compare_digest(
        api_key,
        expected_key,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key",
        )
