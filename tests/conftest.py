import asyncio
import os
from datetime import datetime

import pytest
from httpx import AsyncClient
from alembic.config import Config
from alembic.command import upgrade
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine

from app import main, models, schema


@pytest.fixture
async def mailing():
    mailing = schema.Mailing(
        id=0,
        clients_tags=[],
        clients_mobile_operator_codes=[],
        text="",
        start_time=datetime.now(),
        end_time=datetime.now(),
    )
    return mailing


@pytest.fixture(scope="session")
def event_loop() -> None:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture
async def client() -> AsyncClient:
    async with AsyncClient(app=main.app, base_url="http://localhost:8000") as c:
        yield c


@pytest.fixture(scope="session")
async def testing_database_url() -> str:
    yield "sqlite+aiosqlite:///test.sqlite3"
    os.remove("test.sqlite3")
    # temp_db_url = check_output(["pg_tmp", "-t"]).decode("utf-8")  # Postgres by pg_tmp
    # temp_db_url = temp_db_url[temp_db_url.find(':'):]
    # temp_db_url = f"postgresql+asyncpg{temp_db_url}"
    # return temp_db_url


@pytest.fixture(scope="session", autouse=True)
def create_test_database_schema(testing_database_url: str) -> None:
    cfg = Config("./alembic.ini")
    cfg.set_main_option("sqlalchemy.url", testing_database_url)
    upgrade(cfg, "head")


@pytest.fixture(scope="session")
async def testing_db_engine(testing_database_url: str) -> AsyncEngine:
    engine = create_async_engine(testing_database_url)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
async def testing_db_session(testing_db_engine: AsyncEngine) -> AsyncSession:
    session = async_sessionmaker(bind=testing_db_engine, autoflush=False, expire_on_commit=False)()
    yield session
    await session.close()


async def clear_db(db_engine: AsyncEngine) -> None:
    async with db_engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.drop_all)
        await conn.run_sync(models.Base.metadata.create_all)


@pytest.fixture(scope="module")
async def testing_database(testing_db_session: AsyncSession,
                           testing_db_engine: AsyncEngine) -> AsyncSession:
    await testing_db_session.close()  # "When the Session is closed, it is essentially in the original state as when it
    # was first constructed, and may be used again. In this sense, the Session.close() method is more like a “reset”
    # back to the clean state and not as much like a “database close” method." - SQLAlchemy 2.0 docs

    await clear_db(testing_db_engine)
    yield testing_db_session


@pytest.fixture
async def clear_testing_database(testing_db_engine: AsyncEngine,
                                 testing_db_session: AsyncSession) -> AsyncSession:
    await testing_db_session.close()  # "When the Session is closed, it is essentially in the original state as when it
    # was first constructed, and may be used again. In this sense, the Session.close() method is more like a “reset”
    # back to the clean state and not as much like a “database close” method." - SQLAlchemy 2.0 docs

    await clear_db(testing_db_engine)
    yield testing_db_session
