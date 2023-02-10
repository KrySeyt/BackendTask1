from unittest.mock import MagicMock, AsyncMock

from src import logging


async def test_log_parsed_request(monkeypatch):
    monkeypatch.setattr(logging, "logger", logger_mock := MagicMock())
    request_mock = AsyncMock()
    request_mock["endpoint"].__name__ = MagicMock()
    request_mock["endpoint"].__module__ = MagicMock()
    request_mock.headers = MagicMock()
    request_mock.headers.get = MagicMock(return_value=None)

    await logging.log_parsed_request(request_mock)

    print(logger_mock.bind.call_args)
    assert logger_mock.bind.call_args.kwargs["request_body_params"] == {}

    logger_mock.reset_mock()
    request_mock.headers.get = MagicMock(return_value="application/x-www-form-urlencoded")
    request_mock.form = AsyncMock(return_value="Result")

    await logging.log_parsed_request(request_mock)

    assert logger_mock.bind.call_args.kwargs["request_body_params"] == "Result"
