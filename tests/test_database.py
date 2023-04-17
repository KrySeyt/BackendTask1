from src.database import get_async_engine


async def test_get_async_engine():
    default_engine1 = get_async_engine()
    default_engine2 = get_async_engine()
    assert default_engine1 == default_engine2

    custom_engine = get_async_engine("postgresql+asyncpg://scott:tiger@localhost:5432/mydatabase")
    assert default_engine1 != custom_engine
