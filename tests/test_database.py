from unittest.mock import MagicMock

from src import database


async def test_get_sessionmaker(monkeypatch):
    settings_mock = MagicMock()
    settings_mock.postgresql_url = "postgresql+psycopg2://scott:tiger@host/dbname"

    sessionmaker = await database.get_sessionmaker()
    session = sessionmaker()
    await session.close()
