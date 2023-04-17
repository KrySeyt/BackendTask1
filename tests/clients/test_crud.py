import pytest
from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from src.mailings import schema as mailings_schema
from src.mailings import models as mailings_models
from src.clients import schema as clients_schema
from src.clients import models as clients_models
from src.clients import crud as clients_crud


async def test_create_client(testing_database: AsyncSession):
    client_schema = clients_schema.ClientIn(
        phone_number="+79999999999",
        phone_operator_code=999,
        tag=mailings_schema.MailingTagIn(
            text="Tag text"
        ),
        timezone="Europe/Amsterdam",
    )

    db_client = await clients_crud.create_client(testing_database, client_schema)
    assert db_client
    db_client_copy = await clients_crud.create_client(testing_database, client_schema)
    assert db_client_copy.tag_id == db_client.tag_id, "Clients tags must be unique"


async def test_get_client_by_phone_number(clear_testing_database: AsyncSession):
    client_schema = clients_schema.ClientIn(
        phone_number="+79999999999",
        phone_operator_code=999,
        tag=mailings_schema.MailingTagIn(
            text="Tag text"
        ),
        timezone="Europe/Amsterdam",
    )
    db_client = await clients_crud.create_client(clear_testing_database, client_schema)

    expected_result = db_client
    result = await clients_crud.get_client_by_phone_number(clear_testing_database, db_client.phone_number)
    assert result == expected_result


async def test_update_client_none(testing_database):
    client = clients_schema.ClientInWithID(
        id=2,
        tag=mailings_schema.MailingTagIn(text="Tag"),
        phone_number="+79009999999",
        phone_operator_code=900,
        timezone="Europe/Amsterdam",
    )

    expected_result = None
    result = await clients_crud.update_client(testing_database, client)
    assert result == expected_result


async def test_delete_client_none(testing_database):
    non_existent_client_id = 2
    expected_result = None
    result = await clients_crud.delete_client(testing_database, non_existent_client_id)
    assert result == expected_result


async def test_get_clients_by_tag(testing_database):
    db_tag = (await testing_database.execute(select(mailings_models.MailingTag).
                                             where(mailings_models.MailingTag.text == "Tag text"))).scalar()

    tag = mailings_schema.MailingTag.from_orm(db_tag)

    stmt = select(clients_models.Client).join(clients_models.MailingTag).where(mailings_models.MailingTag.id == tag.id)
    expected_result = (await testing_database.execute(stmt)).scalars().all()

    result = await clients_crud.get_clients_by_tag(testing_database, tag)

    assert result == expected_result


async def test_get_clients_by_tags(testing_database):
    tags = (await testing_database.execute(select(mailings_models.MailingTag))).scalars().all()
    tags_id = map(lambda x: x.id, tags)

    stmt = select(clients_models.Client).join(mailings_models.MailingTag).\
        where(mailings_models.MailingTag.id.in_(tags_id))
    expected_result = (await testing_database.scalars(stmt)).all()

    result = await clients_crud.get_clients_by_tags(testing_database,
                                                    [mailings_schema.MailingTag.from_orm(tag) for tag in tags])
    assert result == expected_result


async def test_get_clients_by_phone_code(testing_database):
    phone_code = (await testing_database.scalar(select(clients_models.Client.phone_operator_code)))

    stmt = select(clients_models.Client).where(clients_models.Client.phone_operator_code == phone_code)
    expected_result = list((await testing_database.scalars(stmt)).all())

    result = await clients_crud.get_clients_by_phone_code(testing_database, phone_code)

    assert result == expected_result


async def test_get_clients_by_phone_codes(testing_database):
    phone_codes = (await testing_database.scalars(select(clients_models.Client.phone_operator_code))).all()

    stmt = select(clients_models.Client).where(clients_models.Client.phone_operator_code.in_(phone_codes))
    expected_result = list((await testing_database.scalars(stmt)).all())

    result = await clients_crud.get_clients_by_phone_codes(testing_database, phone_codes)

    assert result == expected_result
