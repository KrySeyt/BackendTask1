from unittest.mock import AsyncMock, MagicMock

from app import config
from app.mailing_service import sending, clients, messages


async def test_get_sending(mailing):
    sending_ = sending.Sending(mailing)
    assert await sending.Sending.get_sending(mailing) == sending_


async def test_start(mailing, monkeypatch):
    sending_ = sending.Sending(mailing)

    monkeypatch.setattr(clients, "get_clients_by_tags", get_client_by_tags_mock := AsyncMock(return_value=[1, 2, 3]))
    monkeypatch.setattr(clients, "get_clients_by_phone_codes", get_client_by_phone_mock := AsyncMock(return_value=[4, 5, 6]))
    monkeypatch.setattr(messages, "create_message", create_message_mock := AsyncMock())

    await sending_.start(AsyncMock(), MagicMock())

    get_client_by_tags_mock.assert_called()
    get_client_by_phone_mock.assert_called()
    create_message_mock.assert_called()


async def test_stop(mailing):
    sending_ = sending.Sending(mailing)

    request_tasks = [MagicMock() for _ in range(3)]
    sending_.request_tasks = request_tasks

    await sending_.stop()

    for task in request_tasks:
        task.cancel.assert_called()


async def test_send_timeout(mailing, monkeypatch):
    settings_mock = MagicMock()
    settings_mock.successful_status_codes = [200]

    endpoint_mock = MagicMock()
    endpoint_mock.send = AsyncMock(return_value=200)

    monkeypatch.setattr(config, "get_settings", lambda: settings_mock)
    monkeypatch.setattr(sending.asyncio, "sleep", sleep_mock := AsyncMock())

    sending_ = sending.Sending(mailing)
    await sending_._send(db_mock := AsyncMock(), endpoint_mock, MagicMock(), MagicMock())

    sleep_mock.assert_awaited()
    endpoint_mock.send.assert_awaited()
    db_mock.commit.assert_awaited()
