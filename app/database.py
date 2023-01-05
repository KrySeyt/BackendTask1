import os

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DATABASE_POSTGRESQL_ENV_VAR_NAME: str = "BackendTask1HerokuPostgresURL"
DATABASE_URL_DATA: str = os.getenv(
    DATABASE_POSTGRESQL_ENV_VAR_NAME
)[os.getenv(DATABASE_POSTGRESQL_ENV_VAR_NAME).find(':'):]  # type: ignore
SQLALCHEMY_DATABASE_URL: str = f"postgresql+asyncpg{DATABASE_URL_DATA}"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()
