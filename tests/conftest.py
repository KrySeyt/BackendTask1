import asyncio
from datetime import datetime

import pytest
from httpx import AsyncClient

from app import main
from app.mailing_service import schema


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
