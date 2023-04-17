from functools import lru_cache

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import DeclarativeBase

from src.config import get_settings


class Base(DeclarativeBase):
    pass


def get_sqlalchemy_postgres_url() -> str:
    postgres_url = get_settings().postgresql_url
    database_url_data = postgres_url[postgres_url.find(':'):]
    sqlalchemy_database_url = f"postgresql+asyncpg{database_url_data}"
    return sqlalchemy_database_url


@lru_cache(maxsize=1)
def get_async_engine(postgres_url: str | None = None) -> AsyncEngine:
    db_url = postgres_url
    if not db_url:
        db_url = get_sqlalchemy_postgres_url()
    return create_async_engine(db_url)
