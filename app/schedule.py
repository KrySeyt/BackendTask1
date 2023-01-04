from datetime import datetime
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from .schema import Mailing
from .sending import Sending
from .endpoints import Endpoint


class Schedule:
    tasks: dict[Mailing, asyncio.Task[None]] = dict()
    expired_tasks_delition: dict[Mailing, asyncio.Task[None]] = dict()
    tasks_lock = asyncio.Lock()
    expired_tasks_delition_lock = asyncio.Lock()

    @staticmethod
    async def mailing_task(db: AsyncSession, mailing: Mailing, endpoint: Endpoint) -> None:
        if mailing.end_time.timestamp() < datetime.now().timestamp():
            return
        if mailing.start_time.timestamp() > datetime.now().timestamp():
            await asyncio.sleep(mailing.start_time.timestamp() - datetime.now().timestamp())
        await Sending(mailing).start(db, endpoint)

    @classmethod
    async def delete_expired_task(cls, mailing: Mailing) -> None:
        await asyncio.sleep(mailing.end_time.timestamp() - datetime.now().timestamp())
        async with cls.tasks_lock:
            cls.tasks.pop(mailing).cancel()
        async with cls.expired_tasks_delition_lock:
            cls.expired_tasks_delition.pop(mailing)

    @classmethod
    async def add_mailing_to_schedule(cls, db: AsyncSession, mailing: Mailing, endpoint: Endpoint) -> None:
        async with cls.tasks_lock:
            cls.tasks[mailing] = asyncio.create_task(cls.mailing_task(db, mailing, endpoint))
        async with cls.expired_tasks_delition_lock:
            cls.expired_tasks_delition[mailing] = asyncio.create_task(cls.delete_expired_task(mailing))

    @classmethod
    async def delete_mailing_from_schedule(cls, mailing: Mailing) -> None:
        if mailing in cls.tasks:
            async with cls.tasks_lock:
                cls.tasks.pop(mailing).cancel()
        if mailing in cls.expired_tasks_delition:
            async with cls.expired_tasks_delition_lock:
                cls.expired_tasks_delition.pop(mailing).cancel()
