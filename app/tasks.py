from datetime import datetime
import asyncio

from .schema import Mailing
from .sending import start_sending


tasks: dict[Mailing, asyncio.Task] = dict()


async def mailing_task(mailing: Mailing) -> None:
    if mailing.end_time.timestamp() <= datetime.now().timestamp():
        return
    if mailing.start_time.timestamp() > datetime.now().timestamp():
        await asyncio.sleep((mailing.start_time.timestamp() - datetime.now().timestamp()))
    await start_sending(mailing)


def add_mailing_to_schedule(mailing: Mailing) -> None:
    tasks[mailing] = asyncio.create_task(mailing_task(mailing))


def delete_mailing_from_schedule(mailing: Mailing) -> None:
    tasks.pop(mailing)
