from unittest.mock import AsyncMock, MagicMock

from app import clients


async def test_get_client_by_phone_number(monkeypatch):
    expected_result = None
    phone_number = 0
    monkeypatch.setattr(clients.crud, "get_client_by_phone_number", crud_mock := AsyncMock(return_value=expected_result))

    result = await clients.get_client_by_phone_number(db_mock := AsyncMock(), phone_number)
    assert result == expected_result
    crud_mock.assert_awaited_once_with(db_mock, phone_number)

    crud_mock.reset_mock()

    expected_result = "Result"
    crud_mock.return_value = "ClientModel"
    monkeypatch.setattr(clients.schema.Client, "from_orm", from_orm_mock := MagicMock(return_value=expected_result))

    result = await clients.get_client_by_phone_number(db_mock, phone_number)

    assert result == expected_result
    crud_mock.assert_awaited_once_with(db_mock, phone_number)
    from_orm_mock.assert_called_once_with(crud_mock.return_value)


async def test_update_client_none(monkeypatch):
    expected_result = None
    monkeypatch.setattr(clients.crud, "update_client", crud_mock := AsyncMock(return_value=expected_result))

    result = await clients.update_client(db_mock := AsyncMock(), client_mock := MagicMock())
    assert result == expected_result
    crud_mock.assert_awaited_once_with(db_mock, client_mock)


async def test_delete_client_none(monkeypatch):
    expected_result = None
    client_id = 0
    monkeypatch.setattr(clients.crud, "delete_client", crud_mock := AsyncMock(return_value=expected_result))

    result = await clients.delete_client(db_mock := AsyncMock(), client_id)
    assert result == expected_result
    crud_mock.assert_awaited_once_with(db_mock, client_id)


async def test_get_clients_by_tag(monkeypatch):
    expected_result = ["Result"]
    monkeypatch.setattr(clients.crud, "get_clients_by_tag", crud_mock := AsyncMock(return_value=["client"]))
    monkeypatch.setattr(clients.schema.Client, "from_orm", from_orm_mock := MagicMock(return_value="Result"))

    result = await clients.get_clients_by_tag(db_mock := AsyncMock(), tag_mock := MagicMock())

    assert result == expected_result
    crud_mock.assert_awaited_once_with(db_mock, tag_mock)
    for i in crud_mock.return_value:
        from_orm_mock.assert_any_call(i)


async def test_get_clients_by_tags(monkeypatch):
    expected_result = ["Result", "Result"]

    crud_mock = AsyncMock(return_value=["client1", "client2"])
    from_orm_mock = MagicMock(return_value="Result")
    monkeypatch.setattr(clients.crud, "get_clients_by_tags", crud_mock)
    monkeypatch.setattr(clients.schema.Client, "from_orm", from_orm_mock)

    result = await clients.get_clients_by_tags(db_mock := AsyncMock(), tags_mock := [MagicMock()])

    assert result == expected_result
    crud_mock.assert_awaited_once_with(db_mock, tags_mock)
    for i in crud_mock.return_value:
        from_orm_mock.assert_any_call(i)


async def test_get_clients_by_phone_code(monkeypatch):
    expected_result = ["Result"]
    monkeypatch.setattr(clients.crud, "get_clients_by_phone_code", crud_mock := AsyncMock(return_value=["client"]))
    monkeypatch.setattr(clients.schema.Client, "from_orm", from_orm_mock := MagicMock(return_value="Result"))

    result = await clients.get_clients_by_phone_code(db_mock := AsyncMock(), tag_mock := MagicMock())

    assert result == expected_result
    crud_mock.assert_awaited_once_with(db_mock, tag_mock)
    for i in crud_mock.return_value:
        from_orm_mock.assert_any_call(i)


async def test_get_clients_by_phone_codes(monkeypatch):
    expected_result = ["Result", "Result"]

    crud_mock = AsyncMock(return_value=["client", "client2"])
    from_orm_mock = MagicMock(return_value="Result")
    monkeypatch.setattr(clients.crud, "get_clients_by_phone_codes", crud_mock)
    monkeypatch.setattr(clients.schema.Client, "from_orm", from_orm_mock)

    result = await clients.get_clients_by_phone_codes(db_mock := AsyncMock(), tags_mock := [MagicMock()])

    assert result == expected_result
    crud_mock.assert_awaited_once_with(db_mock, tags_mock)
    for i in crud_mock.return_value:
        from_orm_mock.assert_any_call(i)
