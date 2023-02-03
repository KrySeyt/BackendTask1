from unittest.mock import AsyncMock, MagicMock

from app import messages


async def test_create_message(monkeypatch):
    expected_result = "Result"
    monkeypatch.setattr(messages.crud, "create_message", crud_mock := AsyncMock())
    monkeypatch.setattr(messages.schema.Message, "from_orm", schema_mock := MagicMock(return_value=expected_result))

    result = await messages.create_message(AsyncMock(), MagicMock(), MagicMock())

    assert result == expected_result
    crud_mock.assert_awaited_once()
    schema_mock.assert_called_once()
