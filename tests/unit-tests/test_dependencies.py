import pytest

from app.dependencies import get_db_stub, get_endpoint_stub


async def test_get_db_stub():
    with pytest.raises(NotImplementedError):
        await get_db_stub()


async def test_get_endpoint_stub():
    with pytest.raises(NotImplementedError):
        await get_endpoint_stub()
