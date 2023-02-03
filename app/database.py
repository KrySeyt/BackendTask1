from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from .config import get_settings


DATABASE_URL_DATA = get_settings().postgresql_url[get_settings().postgresql_url.find(':'):]
SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg{DATABASE_URL_DATA}"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
)
SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
