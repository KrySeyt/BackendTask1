from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from .config import get_settings


async def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    postgres_url = get_settings().postgresql_url

    if not isinstance(postgres_url, str):
        raise TypeError("BACKENDTASK1_POSTGRESQL_URL is not str")

    database_url_data = postgres_url[postgres_url.find(':'):]
    sqlalchemy_database_url = f"postgresql+asyncpg{database_url_data}"

    engine = create_async_engine(
        sqlalchemy_database_url,
    )
    return async_sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
