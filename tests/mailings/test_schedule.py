import datetime
from unittest.mock import MagicMock, AsyncMock

from src.mailings import schedule


async def test_mailing_task(mailing, monkeypatch):
    seconds_before_sending = 20
    mailing.start_time += datetime.timedelta(seconds=seconds_before_sending)
    mailing.end_time += datetime.timedelta(seconds=seconds_before_sending + 10)

    sending_mock = MagicMock()
    sending_mock.start = AsyncMock()
    monkeypatch.setattr(schedule, "Sending", lambda *args, **kwargs: sending_mock)
    monkeypatch.setattr(schedule.asyncio, "sleep", sleep_mock := AsyncMock())

    await schedule.Schedule.mailing_task(AsyncMock(), mailing, AsyncMock())

    sleep_mock.assert_awaited_once()
    assert int(sleep_mock.await_args.args[0]) == seconds_before_sending - 1
    sending_mock.start.assert_awaited_once()

    seconds_before_sending = 0
    mailing.start_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds_before_sending)
    mailing.end_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds_before_sending + 10)

    sleep_mock.reset_mock()
    sending_mock.start.reset_mock()

    await schedule.Schedule.mailing_task(AsyncMock(), mailing, AsyncMock())

    sleep_mock.assert_not_awaited()
    sending_mock.start.assert_awaited_once()
