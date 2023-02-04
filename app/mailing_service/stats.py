from collections import Counter

from sqlalchemy.ext.asyncio import AsyncSession

from app.mailing_service import mailings, schema


async def get_stats(db: AsyncSession) -> list[schema.MailingStats]:
    stats = []
    for mailing in await mailings.get_all_mailings(db):
        messages = await mailings.get_mailing_messages(db, mailing.id)
        messages_dict = dict(Counter((message.status for message in messages)))
        for sts in schema.MessageStatus:
            if sts not in messages_dict:
                messages_dict[sts] = 0
        stats.append(schema.MailingStats(mailing=mailing, messages=messages_dict))
    return stats


async def get_mailing_stats(db: AsyncSession, mailing: schema.Mailing) -> schema.DetailMailingStats | None:
    messages = await mailings.get_mailing_messages(db, mailing.id)
    return schema.DetailMailingStats(mailing=mailing, messages=messages)
