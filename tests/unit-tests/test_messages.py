from unittest.mock import AsyncMock, MagicMock

from app.mailing_service import messages, schema
from app.database import crud


async def test_create_message(monkeypatch):
    expected_result = "Result"
    monkeypatch.setattr(crud, "create_message", crud_mock := AsyncMock())
    monkeypatch.setattr(schema.Message, "from_orm", schema_mock := MagicMock(return_value=expected_result))

    result = await messages.create_message(AsyncMock(), MagicMock(), MagicMock())

    assert result == expected_result
    crud_mock.assert_awaited_once()
    schema_mock.assert_called_once()
