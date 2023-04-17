import asyncio
from datetime import datetime

import pytest
from httpx import AsyncClient
from alembic.config import Config
from alembic.command import upgrade
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine

from src import main
from src.mailings import schema
from src.database import Base
from src.dependencies import get_db, get_async_engine


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


async def clear_db(db_engine: AsyncEngine) -> None:
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="module", autouse=True)
async def clear_db_at_module_start() -> None:
    await clear_db(get_async_engine())


@pytest.fixture()
async def testing_database() -> AsyncSession:
    session = await get_db()
    yield session
    await session.close()


@pytest.fixture
async def clear_testing_database() -> AsyncSession:
    await clear_db(get_async_engine())
    session = await get_db()
    yield session
    await session.close()


