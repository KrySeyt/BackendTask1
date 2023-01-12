from functools import lru_cache

from pydantic import BaseSettings, PostgresDsn, AnyHttpUrl
from fastapi import status


class Settings(BaseSettings):
    postgresql_url: PostgresDsn
    endpoint_url: AnyHttpUrl | None = None
    successful_status_codes: set[int] = {status.HTTP_200_OK}
    max_requests_at_time: int = 20

    class Config:
        env_prefix = "BackendTask1_"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
