import pytest

from src.dependencies import get_db_stub


async def test_get_db_stub():
    with pytest.raises(NotImplementedError):
        await get_db_stub()
