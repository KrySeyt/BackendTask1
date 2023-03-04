import asyncio
from datetime import datetime

import pytest
from httpx import AsyncClient
from alembic.config import Config
from alembic.command import upgrade
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine

from src import main
from src.mailings import schema
from src.database import Base, get_async_engine, get_sessionmaker


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


@pytest.fixture(scope="session", autouse=True)
def create_test_database_schema() -> None:
    cfg = Config("./alembic.ini")
    upgrade(cfg, "head")


@pytest.fixture(scope="session")
async def testing_db_engine() -> AsyncEngine:
    engine = await get_async_engine()
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
async def testing_db_session(testing_db_engine: AsyncEngine) -> AsyncSession:
    sessionmaker = await get_sessionmaker(testing_db_engine)
    session = sessionmaker()
    yield session
    await session.close()


async def clear_db(db_engine: AsyncEngine) -> None:
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="module")
async def testing_database(testing_db_session: AsyncSession,
                           testing_db_engine: AsyncEngine) -> AsyncSession:
    await testing_db_session.close()  # "When the Session is closed, it is essentially in the original state as when it
    # was first constructed, and may be used again. In this sense, the Session.close() method is more like a “reset”
    # back to the clean state and not as much as a “database close” method." - SQLAlchemy 2.0 docs

    await clear_db(testing_db_engine)
    yield testing_db_session


@pytest.fixture
async def clear_testing_database(testing_db_session: AsyncSession,
                                 testing_db_engine: AsyncEngine) -> AsyncSession:
    await testing_db_session.close()  # "When the Session is closed, it is essentially in the original state as when it
    # was first constructed, and may be used again. In this sense, the Session.close() method is more like a “reset”
    # back to the clean state and not as much as a “database close” method." - SQLAlchemy 2.0 docs

    await clear_db(testing_db_engine)
    yield testing_db_session


