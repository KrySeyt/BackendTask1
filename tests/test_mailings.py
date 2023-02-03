from unittest.mock import AsyncMock, MagicMock

from app import mailings


async def test_get_mailing_tag(monkeypatch):
    expected_result = None
    monkeypatch.setattr(mailings.crud, "get_mailing_tag", crud_mock := AsyncMock(return_value=None))

    result = await mailings.get_mailing_tag(db_mock := AsyncMock(), tag_text_mock := MagicMock())

    assert expected_result == result
    crud_mock.assert_awaited_once_with(db_mock, tag_text_mock)

    expected_result = "Result"
    crud_mock.reset_mock()
    crud_mock.return_value = "db_tag"
    monkeypatch.setattr(mailings.schema.MailingTag, "from_orm", from_orm_mock := MagicMock(return_value="Result"))

    result = await mailings.get_mailing_tag(db_mock, tag_text_mock)

    assert result == expected_result
    crud_mock.assert_awaited_once_with(db_mock, tag_text_mock)
    from_orm_mock.assert_called_once_with(crud_mock.return_value)


async def test_update_mailing_none(monkeypatch):
    expected_result = None
    monkeypatch.setattr(mailings.crud, "get_mailing_by_id", crud_mock := AsyncMock(return_value=None))

    result = await mailings.update_mailing(db_mock := AsyncMock(),
                                           mailing_mock := MagicMock(),
                                           AsyncMock())

    assert result == expected_result
    crud_mock.assert_awaited_once_with(db_mock, mailing_mock.id)


async def test_update_mailing_stop_sending(monkeypatch):
    monkeypatch.setattr(mailings.crud, "get_mailing_by_id", AsyncMock(return_value="mailing"))
    monkeypatch.setattr(mailings.schema.Mailing, "from_orm", AsyncMock())
    monkeypatch.setattr(mailings.Schedule, "delete_mailing_from_schedule", AsyncMock())
    sending_mock = AsyncMock()
    monkeypatch.setattr(mailings.Sending, "get_sending", AsyncMock(return_value=sending_mock))
    monkeypatch.setattr(mailings.crud, "update_mailing", AsyncMock(return_value=None))
    monkeypatch.setattr(mailings.schema.Mailing, "from_orm", MagicMock())
    monkeypatch.setattr(mailings.Schedule, "add_mailing_to_schedule", AsyncMock())

    await mailings.update_mailing(AsyncMock(), AsyncMock(), AsyncMock())
    sending_mock.stop.assert_awaited_once_with()
