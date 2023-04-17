from datetime import datetime
from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from src.mailings import schema as mailings_schema
from src.clients import schema as clients_schema
from src.mailings import models as mailings_models
from src.mailings import crud as mailings_crud


async def test_create_mailing(testing_database: AsyncSession):
    mailing_schema = mailings_schema.MailingIn(
        clients_tags=[mailings_schema.MailingTagIn(text=i) for i in ("tag1", "tag2")],
        clients_mobile_operator_codes=[900, 910],
        text="mailing text",
        start_time=datetime.now(),
        end_time=datetime.now(),
    )
    db_mailing = await mailings_crud.create_mailing(testing_database, mailing_schema)
    db_mailing_clone = await mailings_crud.create_mailing(testing_database, mailing_schema)

    assert db_mailing_clone.clients_tags == db_mailing.clients_tags
    assert db_mailing_clone.clients_mobile_operator_codes == db_mailing.clients_mobile_operator_codes


async def test_get_tags_by_texts(clear_testing_database):
    tags = [mailings_models.MailingTag(text=text) for text in ("First", "Second", "Third")]
    for tag in tags:
        clear_testing_database.add(tag)
    await clear_testing_database.commit()

    tags_texts = ("First", "Third")
    expected_result = [tags[0], tags[2]]

    result = await mailings_crud.get_tags_by_texts(clear_testing_database, tags_texts)

    assert result == expected_result


async def test_delete_mailing_none(testing_database):
    non_existent_mailing_id = 1
    expected_result = None
    result = await mailings_crud.delete_mailing(testing_database, non_existent_mailing_id)
    assert result == expected_result


async def test_update_mailing_none(testing_database):
    mailing = mailings_schema.MailingInWithID(
        id=1,
        clients_tags=[],
        clients_mobile_operator_codes=[],
        start_time=datetime.now(),
        end_time=datetime.now(),
        text="",
    )

    expected_result = None
    result = await mailings_crud.update_mailing(testing_database, mailing)
    assert result == expected_result


async def test_update_mailing_mailing(testing_database):
    mailing = mailings_schema.MailingIn(
        clients_tags=[mailings_schema.MailingTagIn(text=i) for i in ("tag1", "tag2")],
        clients_mobile_operator_codes=[900, 910],
        text="mailing text",
        start_time=datetime.now(),
        end_time=datetime.now(),
    )
    db_mailing = await mailings_crud.create_mailing(testing_database, mailing)

    testing_database.add(db_mailing)
    await testing_database.commit()

    new_tags = ("tag1", "tag3")
    new_codes = [900, 950]

    mailing = mailings_schema.Mailing.from_orm(db_mailing)
    mailing_in = mailings_schema.MailingInWithID(**mailing.dict())
    mailing_in.clients_mobile_operator_codes = new_codes
    mailing_in.clients_tags = [mailings_schema.MailingTagIn(text=text) for text in new_tags]

    result_mailing = await mailings_crud.update_mailing(testing_database, mailing_in)

    assert result_mailing.clients_mobile_operator_codes == new_codes
    assert tuple(map(lambda x: x.text, result_mailing.clients_tags)) == new_tags


async def test_create_message(testing_database):
    now = datetime.now()

    mailing = mailings_schema.Mailing(
        id=0,
        clients_tags=[
            mailings_schema.MailingTag(id=0, text="text1"),
            mailings_schema.MailingTag(id=1, text="text2")
        ],
        clients_mobile_operator_codes=[900, 910],
        text="text",
        start_time=now,
        end_time=now,
    )
    client = clients_schema.Client(
        id=0,
        tag=mailings_schema.MailingTag(id=0, text="text=1"),
        phone_number="+79009999999",
        phone_operator_code=900,
        timezone="Europe/Amsterdam",
    )

    result = await mailings_crud.create_message(testing_database, mailing, client)
    expected_result = (await testing_database.scalar(select(mailings_models.Message)))

    assert result == expected_result
    assert result.mailing_id == mailing.id
    assert result.client_id == client.id
    assert result.status == mailings_models.MessageStatus.not_delivered
    assert isinstance(result.created_at, datetime)


async def test_change_message_status(clear_testing_database):
    default_status = mailings_schema.MessageStatus.not_delivered
    expected_status = mailings_schema.MessageStatus.delivered

    message = mailings_models.Message(
        created_at=datetime.now(),
        status=default_status,
        mailing_id=0,
        client_id=0,
    )
    clear_testing_database.add(message)
    await clear_testing_database.commit()

    message_copy = await mailings_crud.change_message_status(
        clear_testing_database,
        message.id,
        expected_status,
    )

    await clear_testing_database.refresh(message)

    assert message_copy is message
    assert message.status == expected_status

    message = await mailings_crud.change_message_status(clear_testing_database, 999, expected_status)

    assert message is None
