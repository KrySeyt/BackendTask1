import datetime
from unittest.mock import AsyncMock

from src.mailings import schema, service as mailings_service


async def test_get_stats(clear_testing_database, monkeypatch):
    mailings_list = [schema.Mailing(id=i, text="Mailing text", start_time=datetime.datetime.now(),
                               end_time=datetime.datetime.now()) for i in range(3)]
    messages = [
        schema.Message(id=0, created_at=datetime.datetime.now(), status=schema.MessageStatus.delivered, mailing_id=0,
                       client_id=0),  # messages should contain NOT all MessageStatus'es
    ]

    monkeypatch.setattr(mailings_service, "get_all_mailings", AsyncMock(return_value=mailings_list))
    monkeypatch.setattr(mailings_service, "get_mailing_messages", AsyncMock(return_value=messages))

    messages_stats = {
        schema.MessageStatus.delivered: 1,
        schema.MessageStatus.not_delivered: 0
    }

    expected_result = [schema.MailingStats(mailing=mailing, messages=messages_stats) for mailing in mailings_list]

    result = await mailings_service.get_stats(AsyncMock())

    assert result == expected_result
