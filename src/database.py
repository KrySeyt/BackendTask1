from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine
from sqlalchemy.orm import DeclarativeBase

from src.config import get_settings


class Base(DeclarativeBase):
    pass


def get_sqlalchemy_postgres_url() -> str:
    postgres_url = get_settings().postgresql_url
    database_url_data = postgres_url[postgres_url.find(':'):]
    sqlalchemy_database_url = f"postgresql+asyncpg{database_url_data}"
    return sqlalchemy_database_url


async def get_async_engine() -> AsyncEngine:
    return create_async_engine(get_sqlalchemy_postgres_url())


async def get_sessionmaker(engine: AsyncEngine | None = None) -> async_sessionmaker[AsyncSession]:
    if not engine:
        engine = await get_async_engine()
    return async_sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
