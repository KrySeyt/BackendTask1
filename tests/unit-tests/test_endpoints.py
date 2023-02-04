import builtins
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.mailing_service import endpoints


async def test_abstract_endpoint(monkeypatch):
    assert "send" in endpoints.Endpoint.__abstractmethods__

    monkeypatch.setattr(endpoints.Endpoint, "__abstractmethods__", set())

    endpoint = endpoints.Endpoint()
    with pytest.raises(NotImplementedError):
        await endpoint.send(MagicMock(), MagicMock(), MagicMock())


async def test_apiendpoint(monkeypatch):
    url = "url"
    endpoint = endpoints.APIEndpoint(url)

    response_mock = MagicMock()
    response_mock.status = 200

    async def get_response(*args, **kwargs):
        return response_mock

    coro_mock = AsyncMock()
    coro_mock.__aenter__ = get_response
    post_mock = MagicMock(return_value=coro_mock)

    monkeypatch.setattr(endpoints.aiohttp.ClientSession, "post", post_mock)

    message_mock = MagicMock()
    message_mock.id = 1
    client_mock = MagicMock()
    client_mock.phone_number = "+71111111111"
    mailing_mock = MagicMock()
    mailing_mock.text = "mailing text"

    status_code = await endpoint.send(message_mock, client_mock, mailing_mock)

    post_mock.assert_called_with("url/send/1", json={
        "id": 1,
        "phone": 71111111111,
        "text": "mailing text"
    })

    assert status_code == response_mock.status


async def test_testendpoint(monkeypatch):
    endpoint = endpoints.TestEndpoint()

    print_mock = MagicMock()
    monkeypatch.setattr(builtins, "print", print_mock)

    status_code = await endpoint.send(MagicMock(), MagicMock(), MagicMock())

    assert status_code == 200
    print_mock.assert_called()
