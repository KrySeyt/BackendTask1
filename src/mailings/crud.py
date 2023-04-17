import datetime
from typing import Iterable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.clients import schema as clients_schema
from . import schema
from . import models


async def get_tags_by_texts(db: AsyncSession, tags: Iterable[str]) -> list[models.MailingTag]:
    stmt = select(models.MailingTag).where(models.MailingTag.text.in_(tags))
    db_tags = await db.execute(stmt)
    return list(db_tags.scalars().all())


async def create_mailing_tag(db: AsyncSession, tag: schema.MailingTagIn) -> models.MailingTag:
    db_mailing_tag = models.MailingTag(**tag.dict())
    db.add(db_mailing_tag)
    await db.commit()
    await db.refresh(db_mailing_tag)
    return db_mailing_tag


async def create_mailing_tags(db: AsyncSession, tags: Iterable[schema.MailingTagIn]) -> list[models.MailingTag]:
    db_tags = []
    for tag_schema in tags:
        db_tags.append(models.MailingTag(**tag_schema.dict()))

    db.add_all(db_tags)
    await db.commit()

    for db_tab in db_tags:
        await db.refresh(db_tab)

    return db_tags


async def get_mailing_tag(db: AsyncSession, tag_text: str) -> models.MailingTag | None:
    stmt = select(models.MailingTag).filter(models.MailingTag.text == tag_text)
    db_mailing_tag1 = await db.execute(stmt)
    db_mailing_tag = (await db.execute(stmt)).scalar()
    return db_mailing_tag


async def get_operator_code(db: AsyncSession, code: int) -> models.MailingMobileOperatorCode | None:
    return (await db.execute(select(models.MailingMobileOperatorCode).filter(
        models.MailingMobileOperatorCode.code == code))).scalar()


async def get_operator_codes(db: AsyncSession, codes: Iterable[int]) -> list[models.MailingMobileOperatorCode]:
    return list((await db.execute(select(models.MailingMobileOperatorCode).filter(
        models.MailingMobileOperatorCode.code.in_(codes)))).scalars())


async def create_mailing(db: AsyncSession, mailing: schema.MailingIn) -> models.Mailing:
    existed_tags = await get_tags_by_texts(db, map(lambda x: x.text, mailing.clients_tags))
    existed_tags_texts = map(lambda x: x.text, existed_tags)
    not_existed_tags = filter(lambda x: x.text not in existed_tags_texts, mailing.clients_tags)
    clients_tags = existed_tags + await create_mailing_tags(db, not_existed_tags)

    existed_operator_codes = await get_operator_codes(db, mailing.clients_mobile_operator_codes)
    existed_codes_numbers = map(lambda x: x.code, existed_operator_codes)
    not_existed_codes = filter(lambda x: x not in existed_codes_numbers, mailing.clients_mobile_operator_codes)
    operator_codes = existed_operator_codes + [models.MailingMobileOperatorCode(code=i) for i in not_existed_codes]

    db_mailing = models.Mailing(
        text=mailing.text,
        clients_tags=clients_tags,
        clients_mobile_operator_codes=operator_codes,
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
            db_tag = models.MailingTag(text=tag.text)
        clients_tags.append(db_tag)

    clients_operator_codes: list[models.MailingMobileOperatorCode] = []
    for code in mailing.clients_mobile_operator_codes:
        db_code = await get_operator_code(db, code)
        if not db_code:
            db_code = models.MailingMobileOperatorCode(code=code)
        clients_operator_codes.append(db_code)

    db_mailing.text = mailing.text
    db_mailing.start_time = mailing.start_time
    db_mailing.end_time = mailing.end_time
    db_mailing.clients_tags = clients_tags
    db_mailing.clients_mobile_operator_codes = clients_operator_codes  # type: ignore
    # Mypy doesn't handle type that setter expects, only that getter returns

    await db.commit()
    await db.refresh(db_mailing)

    return db_mailing


async def get_all_mailings(db: AsyncSession) -> list[models.Mailing]:
    return list((await db.execute(select(models.Mailing))).scalars().all())


async def get_mailing_messages(db: AsyncSession, mailing_id: int) -> list[models.Message]:
    return list((await db.execute(select(models.Message).filter(
        models.Message.mailing_id == mailing_id))).scalars().all())


async def create_message(db: AsyncSession, mailing: schema.Mailing, client: clients_schema.Client) -> models.Message:
    message = models.Message(
        mailing_id=mailing.id,
        client_id=client.id,
        created_at=datetime.datetime.now(),
        status=schema.MessageStatus.not_delivered,
    )

    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


async def get_message_by_id(db: AsyncSession, message_id: int) -> models.Message | None:
    return await db.get(models.Message, message_id)


async def change_message_status(db: AsyncSession,
                                message_id: int, status:
                                schema.MessageStatus) -> models.Message | None:

    db_message = await get_message_by_id(db, message_id)
    if not db_message:
        return None

    db_message.status = status
    await db.commit()
    await db.refresh(db_message)
    return db_message
