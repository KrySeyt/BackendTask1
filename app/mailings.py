import asyncio

from app.schedule import Schedule
from app.schema import Mailing, MailingIn, MailingInWithID
from app.sending import Sending

from .endpoints import Endpoint

from . import crud


async def delete_mailing(mailing: Mailing):
    await Schedule.delete_mailing_from_schedule(mailing)
    sending = await Sending.get_sending(mailing)
    if sending:
        await sending.stop()
    return crud.delete_mailing(mailing.id)


async def create_mailing(mailing: MailingIn, endpoint: Endpoint) -> Mailing:
    mailing_in_db = crud.create_mailing(mailing)
    asyncio.create_task(Schedule.add_mailing_to_schedule(mailing_in_db, endpoint))
    return mailing_in_db


async def update_mailing(mailing_in_db: Mailing, new_mailing: MailingInWithID) -> Mailing:
    await Schedule.delete_mailing_from_schedule(mailing_in_db)
    sending = await Sending.get_sending(mailing_in_db)
    if sending:
        await sending.stop()
    return crud.update_mailing(new_mailing)
