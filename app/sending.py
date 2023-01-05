from __future__ import annotations
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status

from .endpoints import Endpoint

from .schema import Mailing, Message, Client, MessageStatus
from . import clients
from . import messages


MAX_REQUESTS_AT_TIME = 20


class Sending:
    sendings: dict[Mailing, Sending] = dict()
    request_tasks_semaphore = asyncio.Semaphore(MAX_REQUESTS_AT_TIME)

    def __init__(self, mailing: Mailing):
        self.mailing = mailing
        self.sendings[mailing] = self
        self.request_tasks: list[asyncio.Task[None]] = []

    async def _send(self, db: AsyncSession, endpoint: Endpoint, message: Message, client: Client) -> None:
        sleep_time = 0
        status_code = 0
        while status_code != status.HTTP_200_OK:
            async with self.request_tasks_semaphore:
                try:
                    status_code = await endpoint.send(message, client, self.mailing)
                except asyncio.TimeoutError:
                    pass
            sleep_time += 20
            await asyncio.sleep(sleep_time)
        message.status = MessageStatus.delivered
        await db.commit()

    async def stop(self) -> None:
        for task in self.request_tasks:
            task.cancel()

    async def start(self, db: AsyncSession, endpoint: Endpoint) -> None:
        clients_set = {
            *await clients.get_clients_by_tags(db, self.mailing.clients_tags),
            *await clients.get_clients_by_phone_codes(db, self.mailing.clients_mobile_operator_codes),
        }
        for client in clients_set:
            message = await messages.create_message(db, self.mailing, client)
            self.request_tasks.append(asyncio.create_task(self._send(db, endpoint, message, client)))

    @classmethod
    async def get_sending(cls, mailing: Mailing) -> Sending | None:
        return cls.sendings.get(mailing, None)

