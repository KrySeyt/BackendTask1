import pytest

from src.mailings.dependencies import get_endpoint_stub


async def test_get_endpoint_stub():
    with pytest.raises(NotImplementedError):
        await get_endpoint_stub()
