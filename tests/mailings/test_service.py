from unittest.mock import AsyncMock, MagicMock

from src.mailings import service, schema
from src.mailings import crud
from src.mailings.sending import Sending
from src.mailings.schedule import Schedule


async def test_get_mailing_tag(monkeypatch):
    expected_result = None
    monkeypatch.setattr(crud, "get_mailing_tag", crud_mock := AsyncMock(return_value=None))

    result = await service.get_mailing_tag(db_mock := AsyncMock(), tag_text_mock := MagicMock())

    assert expected_result == result
    crud_mock.assert_awaited_once_with(db_mock, tag_text_mock)

    expected_result = "Result"
    crud_mock.reset_mock()
    crud_mock.return_value = "db_tag"
    monkeypatch.setattr(schema.MailingTag, "from_orm", from_orm_mock := MagicMock(return_value="Result"))

    result = await service.get_mailing_tag(db_mock, tag_text_mock)

    assert result == expected_result
    crud_mock.assert_awaited_once_with(db_mock, tag_text_mock)
    from_orm_mock.assert_called_once_with(crud_mock.return_value)


async def test_update_mailing_none(monkeypatch):
    expected_result = None
    monkeypatch.setattr(crud, "get_mailing_by_id", crud_mock := AsyncMock(return_value=None))

    result = await service.update_mailing(db_mock := AsyncMock(),
                                          mailing_mock := MagicMock(),
                                          AsyncMock())

    assert result == expected_result
    crud_mock.assert_awaited_once_with(db_mock, mailing_mock.id)


async def test_update_mailing_stop_sending(monkeypatch):
    monkeypatch.setattr(crud, "get_mailing_by_id", AsyncMock(return_value="mailing"))
    monkeypatch.setattr(schema.Mailing, "from_orm", AsyncMock())
    monkeypatch.setattr(Schedule, "delete_mailing_from_schedule", AsyncMock())
    sending_mock = AsyncMock()
    monkeypatch.setattr(Sending, "get_sending", AsyncMock(return_value=sending_mock))
    monkeypatch.setattr(crud, "update_mailing", AsyncMock(return_value=None))
    monkeypatch.setattr(schema.Mailing, "from_orm", MagicMock())
    monkeypatch.setattr(Schedule, "add_mailing_to_schedule", AsyncMock())

    await service.update_mailing(AsyncMock(), AsyncMock(), AsyncMock())
    sending_mock.stop.assert_awaited_once_with()


async def test_create_message(monkeypatch):
    expected_result = "Result"
    monkeypatch.setattr(crud, "create_message", crud_mock := AsyncMock())
    monkeypatch.setattr(schema.Message, "from_orm", schema_mock := MagicMock(return_value=expected_result))

    result = await service.create_message(AsyncMock(), MagicMock(), MagicMock())

    assert result == expected_result
    crud_mock.assert_awaited_once()
    schema_mock.assert_called_once()
