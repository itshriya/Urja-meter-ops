
from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Flock Meter API"
    environment: str = "development"
    api_key: SecretStr

    portal_base_url: str = "https://urja-ops.flockenergy.tech"
    portal_username: str
    portal_password: SecretStr

    portal_timeout_seconds: float = 15.0

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


@lru_cache
def get_settings():
    return Settings()
