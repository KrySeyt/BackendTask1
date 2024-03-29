import asyncio
from collections import Counter

from sqlalchemy.ext.asyncio import AsyncSession

from .schedule import Schedule
from .sending import Sending

from .endpoints import Endpoint

from . import schema
from . import crud
from ..clients.schema import Client


async def get_mailing_tag(db: AsyncSession, tag_text: str) -> schema.MailingTag | None:
    db_tag = await crud.get_mailing_tag(db, tag_text)
    if not db_tag:
        return None
    return schema.MailingTag.from_orm(db_tag)


async def delete_mailing(db: AsyncSession, mailing: schema.Mailing) -> schema.Mailing:
    await Schedule.delete_mailing_from_schedule(mailing)
    await db.rollback()
    sending = await Sending.get_sending(mailing)
    if sending:
        await sending.stop()
    await crud.delete_mailing(db, mailing.id)
    return mailing


async def create_mailing(db: AsyncSession, mailing: schema.MailingIn, endpoint: Endpoint) -> schema.Mailing:
    mailing_in_db = await crud.create_mailing(db, mailing)
    mailing_schema = schema.Mailing.from_orm(mailing_in_db)
    task = asyncio.create_task(Schedule.add_mailing_to_schedule(db, mailing_schema, endpoint))
    return mailing_schema


async def get_all_mailings(db: AsyncSession) -> list[schema.Mailing]:
    return list(map(schema.Mailing.from_orm, await crud.get_all_mailings(db)))


async def get_mailing_messages(db: AsyncSession, mailing_id: int) -> list[schema.Message]:
    return list(map(schema.Message.from_orm, await crud.get_mailing_messages(db, mailing_id)))


async def update_mailing(db: AsyncSession,
                         mailing: schema.MailingInWithID,
                         endpoint: Endpoint) -> schema.Mailing | None:
    db_mailing = await crud.get_mailing_by_id(db, mailing.id)
    if not db_mailing:
        return None

    mailing_schema = schema.Mailing.from_orm(db_mailing)

    await Schedule.delete_mailing_from_schedule(mailing_schema)
    sending = await Sending.get_sending(mailing_schema)
    if sending:
        await sending.stop()

    updated_db_mailing = await crud.update_mailing(db, mailing)
    if not updated_db_mailing:
        return None

    updated_mailing_schema = schema.Mailing.from_orm(updated_db_mailing)
    await Schedule.add_mailing_to_schedule(db, updated_mailing_schema, endpoint)
    return updated_mailing_schema


async def get_mailing_by_id(db: AsyncSession, mailing_id: int) -> schema.Mailing | None:
    db_mailing = await crud.get_mailing_by_id(db, mailing_id)
    if not db_mailing:
        return None
    return schema.Mailing.from_orm(db_mailing)


async def get_stats(db: AsyncSession) -> list[schema.MailingStats]:
    stats = []
    for mailing in await get_all_mailings(db):
        messages = await get_mailing_messages(db, mailing.id)
        messages_dict = dict(Counter((message.status for message in messages)))
        for sts in schema.MessageStatus:
            if sts not in messages_dict:
                messages_dict[sts] = 0
        stats.append(schema.MailingStats(mailing=mailing, messages=messages_dict))
    return stats


async def get_mailing_stats(db: AsyncSession, mailing: schema.Mailing) -> schema.DetailMailingStats | None:
    messages = await get_mailing_messages(db, mailing.id)
    return schema.DetailMailingStats(mailing=mailing, messages=messages)


async def create_message(db: AsyncSession, mailing: schema.Mailing, client: Client) -> schema.Message:
    return schema.Message.from_orm(await crud.create_message(db, mailing, client))


async def change_message_status(db: AsyncSession,
                                message: schema.Message,
                                status: schema.MessageStatus) -> schema.Message:

    await crud.change_message_status(db, message.id, status)
    message.status = status
    return message
