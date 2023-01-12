import datetime
from typing import Sequence

from phonenumbers import PhoneNumber
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from . import schema
from . import models


async def get_tags_by_texts(db: AsyncSession, tags: Sequence[str]) -> list[models.MailingTag]:
    return (await db.execute(select(models.MailingTag).where(models.MailingTag.text.in_(tags)))).scalars().all()


async def create_mailing_tag(db: AsyncSession, tag: schema.MailingTagIn) -> models.MailingTag:
    db_mailing_tag = models.MailingTag(**tag.dict())
    db.add(db_mailing_tag)
    await db.commit()
    await db.refresh(db_mailing_tag)
    return db_mailing_tag


async def get_mailing_tag(db: AsyncSession, tag_text: str) -> models.MailingTag | None:
    return (await db.execute(select(models.MailingTag).filter(models.MailingTag.text == tag_text))).scalar()


async def get_operator_code(db: AsyncSession, code: int) -> models.MailingMobileOperatorCode | None:
    return (await db.execute(select(models.MailingMobileOperatorCode).filter(
        models.MailingMobileOperatorCode.code == code))).scalar()


async def create_client(db: AsyncSession, client: schema.ClientIn) -> models.Client:
    db_client = await models.Client.create(
        db=db,
        phone_number=client.phone_number,
        phone_operator_code=client.phone_operator_code,
        tag_text=client.tag.text,
        timezone=client.timezone
    )
    db.add(db_client)
    await db.commit()
    await db.refresh(db_client)
    return db_client


async def get_client_by_id(db: AsyncSession, client_id: int) -> models.Client | None:
    return await db.get(models.Client, client_id)


async def get_client_by_phone_number(db: AsyncSession, phone_number: int) -> models.Client | None:
    return (await db.execute(select(models.Client).filter(
        models.Client.phone_number == phone_number
    ))).scalars().first()


async def get_clients(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[models.Client]:
    return (await db.execute(select(models.Client).offset(skip).limit(limit))).scalars().all()


async def update_client(db: AsyncSession, client: schema.ClientInWithID) -> models.Client | None:
    db_client = await db.get(models.Client, client.id)
    if not db_client:
        return None
    new_tag = await get_mailing_tag(db, client.tag.text) or await create_mailing_tag(db, client.tag)

    db_client.tag_id = new_tag.id
    db_client.tag = new_tag
    db_client.phone_number = PhoneNumber(client.phone_number)
    db_client.phone_operator_code = client.phone_operator_code
    db_client.timezone = client.timezone

    await db.commit()
    await db.refresh(db_client)

    return db_client


async def delete_client(db: AsyncSession, client_id: int) -> models.Client | None:
    db_client = await db.get(models.Client, client_id)
    if not db_client:
        return None
    await db.delete(db_client)
    await db.commit()
    return db_client


async def create_mailing(db: AsyncSession, mailing: schema.MailingIn) -> models.Mailing:
    db_mailing = await models.Mailing.create(
        db=db,
        text=mailing.text,
        clients_tags=[tag.text for tag in mailing.clients_tags],
        clients_mobile_operator_codes=mailing.clients_mobile_operator_codes,
        start_time=mailing.start_time,
        end_time=mailing.end_time,
    )

    db.add(db_mailing)
    await db.commit()
    await db.refresh(db_mailing)
    return db_mailing


async def get_mailing_by_id(db: AsyncSession, mailing_id: int) -> models.Mailing | None:
    return await db.get(models.Mailing, mailing_id)


async def delete_mailing(db: AsyncSession, mailing_id: int) -> models.Mailing | None:
    mailing = await get_mailing_by_id(db, mailing_id)
    if not mailing:
        return None
    await db.delete(mailing)
    await db.commit()
    return mailing


async def update_mailing(db: AsyncSession, mailing: schema.MailingInWithID) -> models.Mailing | None:
    db_mailing = await get_mailing_by_id(db, mailing.id)
    if not db_mailing:
        return None

    clients_tags = []
    for tag in mailing.clients_tags:
        db_tag = await get_mailing_tag(db, tag.text)
        if not db_tag:
            db_tag = models.MailingTag(tag.text)
        clients_tags.append(db_tag)

    clients_operator_codes = []
    for code in mailing.clients_mobile_operator_codes:
        db_code = await get_operator_code(db, code)
        if not db_code:
            db_code = models.MailingMobileOperatorCode(code)
        clients_operator_codes.append(db_code)

    db_mailing.text = mailing.text
    db_mailing.start_time = mailing.start_time
    db_mailing.end_time = mailing.end_time
    db_mailing.clients_tags = clients_tags
    db_mailing.clients_mobile_operator_codes = clients_operator_codes

    await db.commit()
    await db.refresh(db_mailing)

    return db_mailing


async def get_all_mailings(db: AsyncSession) -> list[models.Mailing]:
    return (await db.execute(select(models.Mailing))).scalars().all()


async def get_mailing_messages(db: AsyncSession, mailing_id: int) -> list[models.Message]:
    return (await db.execute(select(models.Message).filter(models.Message.mailing_id == mailing_id))).scalars().all()


async def get_clients_by_tag(db: AsyncSession, tag: schema.MailingTag) -> list[models.Client]:
    return (await db.execute(select(models.Client).filter(models.Client.tag.id == tag.id))).scalars().all()


async def get_clients_by_tags(db: AsyncSession, tags: list[schema.MailingTag]) -> list[models.Client]:
    tags_ids = map(lambda x: x.id, set(tags))
    return (await db.execute(select(models.Client).where(models.Client.tag.id in tags_ids))).scalars().all()


async def get_clients_by_phone_code(db: AsyncSession, phone_code: int) -> list[models.Client]:
    return (await db.execute(select(models.Client).where(
        models.Client.phone_operator_code == phone_code
    ))).scalars().all()


async def get_clients_by_phone_codes(db: AsyncSession, phone_codes: Sequence[int]) -> list[models.Client]:
    return (await db.execute(select(models.Client).where(
        models.Client.phone_operator_code in set(phone_codes)
    ))).scalars().all()


async def create_message(db: AsyncSession, mailing: schema.Mailing, client: schema.Client) -> models.Message:
    message = await models.Message.create(
        mailing_id=mailing.id,
        client_id=client.id,
        created_at=datetime.datetime.now(),
        status=schema.MessageStatus.not_delivered,
    )

    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message
