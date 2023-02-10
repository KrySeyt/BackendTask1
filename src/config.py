from functools import lru_cache

from pydantic import BaseSettings, PostgresDsn, AnyHttpUrl
from fastapi import status


class LoggingSettings(BaseSettings):
    format: str = "<green>{time:YYYY-MM-DDTHH:mm:ss.SSSZ!UTC}</green> | <level>{level:<8}</level>"


class Settings(BaseSettings):
    postgresql_url: PostgresDsn | None = None
    endpoint_url: AnyHttpUrl | None = None
    successful_status_codes: set[int] = {status.HTTP_200_OK}
    max_requests_at_time: int = 20
    logging: LoggingSettings = LoggingSettings()

    class Config:
        env_prefix = "BackendTask1_"
        env_nested_delimiter = "__"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
