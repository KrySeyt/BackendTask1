from unittest.mock import MagicMock

import pytest

from app import database


async def test_get_sessionmaker(monkeypatch):
    settings_mock = MagicMock()
    settings_mock.postgresql_url = MagicMock()
    monkeypatch.setattr(database, "get_settings", lambda *args, **kwargs: settings_mock)
    with pytest.raises(TypeError):
        await database.get_sessionmaker()

    settings_mock.postgresql_url = "postgresql+psycopg2://scott:tiger@host/dbname"

    sessionmaker = await database.get_sessionmaker()
    session = sessionmaker()
    await session.close()
