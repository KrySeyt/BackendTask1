import copy
from unittest.mock import AsyncMock, MagicMock

import pytest
from asgi_lifespan import LifespanManager
from sqlalchemy.ext.asyncio import AsyncSession

from app import main
from app import events
from app import dependencies
from app.database import database
from app.mailing_service import schema, schedule


@pytest.fixture(scope="module", autouse=True)
async def change_main_database(testing_database):
    async def mock_get_db():
        return testing_database

    main.app.dependency_overrides[dependencies.get_db_stub] = mock_get_db


async def test_get_db(monkeypatch):
    settings_mock = MagicMock()
    settings_mock.postgresql_url = "postgresql://scott:tiger@hostname/dbname"
    monkeypatch.setattr(database, "get_settings", lambda *args, **kwargs: settings_mock)
    assert await dependencies.get_db() is await dependencies.get_db()


async def test_startup_shutdown(monkeypatch):
    mock_db = AsyncMock(spec=AsyncSession)
    mock_close = AsyncMock(spec=AsyncSession.close)
    mock_db.close = mock_close

    async def mock_get_db():
        return mock_db

    monkeypatch.setattr(events, "get_db", mock_get_db)
    monkeypatch.setattr(events, "get_all_mailings", mock_get_mailings := AsyncMock(return_value=(1, 2, 3)))
    monkeypatch.setattr(schedule.Schedule, "add_mailing_to_schedule", mock_mailing_to_schedule := AsyncMock())

    async with LifespanManager(main.app):
        pass

    mock_get_mailings.assert_awaited()
    mock_mailing_to_schedule.assert_awaited()
    mock_close.assert_awaited()


async def test_create_client_200(client):
    data = {
        "phone_number": "+79009999999",
        "phone_operator_code": 900,
        "timezone": "Europe/Amsterdam",
        "tag": {
            "text": "Any text"
        }
    }
    expected_result = {
        "id": 1,
        "phone_number": "+79009999999",
        "phone_operator_code": 900,
        "timezone": "Europe/Amsterdam",
        "tag": {
            "text": "Any text"
        }
    }

    response = await client.post(r"client/", json=data)
    result = response.json()

    assert response.status_code == 200
    for key in expected_result:
        assert expected_result[key] == result[key]


async def test_create_client_422(client):
    data = {
        "phone_number": "Number",
        "phone_operator_code": 900,
        "timezone": "Europe/Amsterdam",
        "tag": {
            "text": "Any text"
        }
    }

    response = await client.post(url="client/", json=data)
    result = response.json()

    assert response.status_code == 422
    assert result["body"] == data


async def test_422_error_handler(client):
    data = {
        "phone_number": "Word",
        "phone_operator_code": 900,
        "timezone": "Europe/Amsterdam",
        "tag": {
            "text": "Any text"
        }
    }

    response = await client.post(url="client/", json=data)
    result = response.json()

    assert response.status_code == 422
    assert result["body"] == data
    assert result["params"] == {}
    assert result["detail"] == [{
        "loc": [
            "body",
            "phone_number"
        ],
        "msg": "invalid literal for int() with base 10: 'Word'",
        "type": "value_error"
    }]


async def test_update_client_200(client):
    data = {
        "id": 1,
        "phone_number": "+79000000000",
        "phone_operator_code": 910,
        "timezone": "Europe/Amsterdam",
        "tag": {
            "text": "Just another tag"
        }
    }
    expected_result = data.copy()

    response = await client.put(url="client/", json=data)
    result = response.json()

    assert response.status_code == 200
    assert result == expected_result


async def test_update_client_422(client):
    data = {}

    response = await client.put(url="client/", json=data)

    assert response.status_code == 422


async def test_update_client_404(client):
    data = {
        "id": 99999999,
        "phone_number": "+79000000000",
        "phone_operator_code": 910,
        "timezone": "Europe/Amsterdam",
        "tag": {
            "text": "Just another tag"
        }
    }

    response = await client.put(url="client/", json=data)

    assert response.status_code == 404


async def test_get_client_200(client):
    expected_result = {
        "id": 1,
        "phone_number": "+79000000000",
        "phone_operator_code": 910,
        "timezone": "Europe/Amsterdam",
        "tag": {
            "text": "Just another tag"
        }
    }

    response = await client.get("client/1")

    assert response.status_code == 200
    assert response.json() == expected_result


async def test_get_client_422(client):
    response = await client.get("client/Something")
    assert response.status_code == 422


async def test_get_client_404(client):
    response = await client.get("client/9999")
    assert response.status_code == 404


async def test_get_clients_200(client):
    response = await client.get("clients/")
    result = response.json()

    assert response.status_code == 200
    assert isinstance(result, list)
    schema.ClientOut.parse_obj(result[0])


async def test_get_clients_422(client):
    response = await client.get("clients/?skip=SkipSome")
    assert response.status_code == 422


async def test_delete_client_200(client):
    expected_result = {
        "id": 1,
        "phone_number": "+79000000000",
        "phone_operator_code": 910,
        "timezone": "Europe/Amsterdam",
        "tag": {
            "text": "Just another tag"
        }
    }

    response = await client.delete("client/1")

    assert response.status_code == 200
    assert response.json() == expected_result


async def test_delete_client_404(client):
    response = await client.delete("client/9999")
    assert response.status_code == 404


async def test_delete_client_422(client):
    response = await client.delete("client/Something")
    assert response.status_code == 422


async def test_create_mailing_200(client):
    data = {
        "text": "Mailing text",
        "start_time": "2023-01-27T01:37:40.164000",
        "end_time": "2023-01-27T01:37:40.164000",
        "clients_tags": [
            {
                "text": "Any text"
            }
        ],
        "clients_mobile_operator_codes": [
            900,
            910
        ]
    }
    expected_result = {**copy.deepcopy(data), "id": 1}

    response = await client.post("mailing/", json=data)
    result = response.json()

    assert response.status_code == 200
    assert result == expected_result


async def test_create_mailing_422(client):
    data = {
        "text": "Mailing text",
        "start_time": "2023-01-27T01:37:40.164000",
        "end_time": "2023-01-27T01:37:40.164000",
        "clients_tags": [
            {
                "text": "Any text"
            }
        ],
        "clients_mobile_operator_codes": [
            "Code",
            910
        ]
    }
    expected_result = {
        "detail": [
            {
                "loc": [
                    "body",
                    "clients_mobile_operator_codes",
                    0
                ],
                "msg": "value is not a valid integer",
                "type": "type_error.integer"
            }
        ],
        "body": {
            "text": "Mailing text",
            "start_time": "2023-01-27T01:37:40.164000",
            "end_time": "2023-01-27T01:37:40.164000",
            "clients_tags": [
                {
                    "text": "Any text"
                }
            ],
            "clients_mobile_operator_codes": [
                "Code",
                910
            ]
        },
        "params": {}
    }

    response = await client.post("mailing/", json=data)
    result = response.json()

    assert response.status_code == 422
    assert result == expected_result


# @pytest.mark.order(1)
async def test_update_mailing_200(client):
    data = {
        "id": 1,
        "text": "Another text",
        "start_time": "2023-01-27T01:37:40.164000",
        "end_time": "2023-01-27T01:37:40.164000",
        "clients_tags": [
            {
                "text": "Any text"
            }
        ],
        "clients_mobile_operator_codes": [
            900,
            910
        ]
    }
    expected_result = copy.deepcopy(data)

    response = await client.put("mailing/", json=data)
    result = response.json()

    assert response.status_code == 200
    assert result == expected_result


async def test_update_mailing_422(client):
    data = {
        "id": "Just string",
        "text": "Another text",
        "start_time": "2023-01-27T01:37:40.164000",
        "end_time": "2023-01-27T01:37:40.164000",
        "clients_tags": [
            {
                "text": "Any text"
            }
        ],
        "clients_mobile_operator_codes": [
            900,
            910
        ]
    }

    response = await client.put("mailing/", json=data)

    assert response.status_code == 422


async def test_update_mailing_404(client):
    data = {
        "id": "999999",
        "text": "Another text",
        "start_time": "2023-01-27T01:37:40.164000",
        "end_time": "2023-01-27T01:37:40.164000",
        "clients_tags": [
            {
                "text": "Any text"
            }
        ],
        "clients_mobile_operator_codes": [
            900,
            910
        ]
    }

    response = await client.put("mailing/", json=data)

    assert response.status_code == 404


async def test_get_mailing_200(client):
    expected_result = {
        "id": 1,
        "text": "Another text",
        "start_time": "2023-01-27T01:37:40.164000",
        "end_time": "2023-01-27T01:37:40.164000",
        "clients_tags": [
            {
                "text": "Any text"
            }
        ],
        "clients_mobile_operator_codes": [
            900,
            910
        ]
    }
    response = await client.get("mailing/1")
    result = response.json()

    assert response.status_code == 200
    assert result == expected_result


async def test_get_mailing_422(client):
    response = await client.get("mailing/AnyString")
    assert response.status_code == 422


async def test_get_mailing_404(client):
    response = await client.get("mailing/999999")
    assert response.status_code == 404


async def test_get_stats_200_not_empty(client):
    expected_result = [
        {
            "messages": {
                "delivered": 0,
                "not delivered": 0
            },
            "mailing": {
                "text": "Another text",
                "start_time": "2023-01-27T01:37:40.164000",
                "end_time": "2023-01-27T01:37:40.164000",
                "id": 1,
                "clients_tags": [
                    {
                        "text": "Any text"
                    }
                ],
                "clients_mobile_operator_codes": [
                    900,
                    910
                ]
            }
        }
    ]

    response = await client.get("stats/")
    result = response.json()

    assert response.status_code == 200
    assert result == expected_result


async def test_get_mailing_stats_200(client):
    expected_result = {
        "messages": [],
        "mailing": {
            "text": "Another text",
            "start_time": "2023-01-27T01:37:40.164000",
            "end_time": "2023-01-27T01:37:40.164000",
            "id": 1,
            "clients_tags": [
                {
                    "text": "Any text"
                }
            ],
            "clients_mobile_operator_codes": [
                900,
                910
            ]
        }
    }
    response = await client.get("stats/1")
    result = response.json()

    assert response.status_code == 200
    assert result == expected_result


async def test_get_mailing_stats_422(client):
    response = await client.get("stats/AnyString")
    assert response.status_code == 422


async def test_get_mailing_stats_404(client):
    response = await client.get("stats/999999")
    assert response.status_code == 404


async def test_delete_mailing_200(client):
    expected_result = {
        "id": 1,
        "text": "Another text",
        "start_time": "2023-01-27T01:37:40.164000",
        "end_time": "2023-01-27T01:37:40.164000",
        "clients_tags": [
            {
                "text": "Any text"
            }
        ],
        "clients_mobile_operator_codes": [
            900,
            910
        ]
    }

    response = await client.delete("mailing/1")
    result = response.json()

    assert response.status_code == 200
    assert result == expected_result


async def test_delete_mailing_422(client):
    response = await client.delete("mailing/SomeString")
    assert response.status_code == 422


async def test_delete_mailing_404(client):
    response = await client.delete("mailing/99999")
    assert response.status_code == 404


async def test_get_stats_200_empty(client):
    expected_result = []

    response = await client.get("stats/")
    result = response.json()

    assert response.status_code == 200
    assert result == expected_result
