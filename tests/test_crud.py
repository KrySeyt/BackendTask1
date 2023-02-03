from datetime import datetime
from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schema


async def test_get_tags_by_texts(testing_database: AsyncSession):
    tags = [models.MailingTag(text=text) for text in ("First", "Second", "Third")]
    for tag in tags:
        testing_database.add(tag)
    await testing_database.commit()

    tags_texts = ("First", "Third")
    expected_result = [tags[0], tags[2]]

    result = await crud.get_tags_by_texts(testing_database, tags_texts)

    assert result == expected_result


async def test_get_client_by_phone_number(testing_database: AsyncSession):
    client = await models.Client.create(
        db=testing_database,
        phone_number="+79999999999",
        phone_operator_code=999,
        tag_text="Tag text",
        timezone="Europe/Amsterdam",
    )
    testing_database.add(client)
    await testing_database.commit()

    expected_result = client
    result = await crud.get_client_by_phone_number(testing_database, client.phone_number)
    assert result == expected_result


async def test_update_client_none(testing_database):
    client = schema.ClientInWithID(
        id=2,
        tag=schema.MailingTagIn(text="Tag"),
        phone_number="+79009999999",
        phone_operator_code=900,
        timezone="Europe/Amsterdam",
    )

    expected_result = None
    result = await crud.update_client(testing_database, client)
    assert result == expected_result


async def test_delete_client_none(testing_database):
    non_existent_client_id = 2
    expected_result = None
    result = await crud.delete_client(testing_database, non_existent_client_id)
    assert result == expected_result


async def test_delete_mailing_none(testing_database):
    non_existent_mailing_id = 1
    expected_result = None
    result = await crud.delete_mailing(testing_database, non_existent_mailing_id)
    assert result == expected_result


async def test_update_mailing_none(testing_database):
    mailing = schema.MailingInWithID(
        id=1,
        clients_tags=[],
        clients_mobile_operator_codes=[],
        start_time=datetime.now(),
        end_time=datetime.now(),
        text="",
    )

    expected_result = None
    result = await crud.update_mailing(testing_database, mailing)
    assert result == expected_result


async def test_update_mailing_mailing(testing_database):
    db_mailing = await models.Mailing.create(
        db=testing_database,
        clients_tags=["tag1", "tag2"],
        clients_mobile_operator_codes=[900, 910],
        text="mailing text",
        start_time=datetime.now(),
        end_time=datetime.now(),
    )
    testing_database.add(db_mailing)
    await testing_database.commit()

    new_tags = ("tag1", "tag3")
    new_codes = [900, 950]

    mailing = schema.Mailing.from_orm(db_mailing)
    mailing_in = schema.MailingInWithID(**mailing.dict())
    mailing_in.clients_mobile_operator_codes = new_codes
    mailing_in.clients_tags = [schema.MailingTagIn(text=text) for text in new_tags]

    result_mailing = await crud.update_mailing(testing_database, mailing_in)

    assert result_mailing.clients_mobile_operator_codes == new_codes
    assert tuple(map(lambda x: x.text, result_mailing.clients_tags)) == new_tags


async def test_get_clients_by_tag(testing_database):
    db_tag = (await testing_database.execute(select(models.MailingTag).
                                             where(models.MailingTag.text == "Tag text"))).scalar()

    tag = schema.MailingTag.from_orm(db_tag)

    stmt = select(models.Client).join(models.MailingTag).where(models.MailingTag.id == tag.id)
    expected_result = (await testing_database.execute(stmt)).scalars().all()

    result = await crud.get_clients_by_tag(testing_database, tag)

    assert result == expected_result


async def test_get_clients_by_tags(testing_database):
    tags = (await testing_database.execute(select(models.MailingTag))).scalars().all()
    tags_id = map(lambda x: x.id, tags)

    stmt = select(models.Client).join(models.MailingTag).where(models.MailingTag.id.in_(tags_id))
    expected_result = (await testing_database.scalars(stmt)).all()

    result = await crud.get_clients_by_tags(testing_database, [schema.MailingTag.from_orm(tag) for tag in tags])
    assert result == expected_result


async def test_get_clients_by_phone_code(testing_database):
    phone_code = (await testing_database.scalar(select(models.Client.phone_operator_code)))

    stmt = select(models.Client).where(models.Client.phone_operator_code == phone_code)
    expected_result = list((await testing_database.scalars(stmt)).all())

    result = await crud.get_clients_by_phone_code(testing_database, phone_code)

    assert result == expected_result


async def test_get_clients_by_phone_codes(testing_database):
    phone_codes = (await testing_database.scalars(select(models.Client.phone_operator_code))).all()

    stmt = select(models.Client).where(models.Client.phone_operator_code.in_(phone_codes))
    expected_result = list((await testing_database.scalars(stmt)).all())

    result = await crud.get_clients_by_phone_codes(testing_database, phone_codes)

    assert result == expected_result


async def test_create_message(testing_database):
    now = datetime.now()

    mailing = schema.Mailing(
        id=0,
        clients_tags=[
            schema.MailingTag(id=0, text="text1"),
            schema.MailingTag(id=1, text="text2")
        ],
        clients_mobile_operator_codes=[900, 910],
        text="text",
        start_time=now,
        end_time=now,
    )
    client = schema.Client(
        id=0,
        tag=schema.MailingTag(id=0, text="text=1"),
        phone_number="+79009999999",
        phone_operator_code=900,
        timezone="Europe/Amsterdam",
    )

    result = await crud.create_message(testing_database, mailing, client)
    expected_result = (await testing_database.scalar(select(models.Message)))

    assert result == expected_result
    assert result.mailing_id == mailing.id
    assert result.client_id == client.id
    assert result.status == models.MessageStatus.not_delivered
    assert isinstance(result.created_at, datetime)
