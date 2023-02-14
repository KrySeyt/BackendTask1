from __future__ import annotations
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
# from loguru import logger

from src.clients import service as clients_service
from src.config import get_settings
from src.clients.schema import Client

from .endpoints import Endpoint
from .schema import Mailing, Message, MessageStatus
from . import service as mailings_service


class Sending:
    sendings: dict[Mailing, Sending] = {}
    request_tasks_semaphore = asyncio.Semaphore(get_settings().max_requests_at_time)

    def __init__(self, mailing: Mailing):
        self.mailing = mailing
        self.sendings[mailing] = self
        self.request_tasks: list[asyncio.Task[None]] = []

    async def _send(self, db: AsyncSession, endpoint: Endpoint, message: Message, client: Client) -> None:
        sleep_time = 0
        status_code = 0
        while status_code not in get_settings().successful_status_codes:
            await asyncio.sleep(sleep_time)
            async with self.request_tasks_semaphore:
                try:
                    status_code = await endpoint.send(message, client, self.mailing)
                except asyncio.TimeoutError:
                    pass

            # logger.bind(
            #     message_sent=True,
            #     sending_status="Success" if status_code in get_settings().successful_status_codes else "Failed",
            #     status_code=status_code,
            # ).info("Message sent")

            sleep_time += 20
        message.status = MessageStatus.delivered
        await db.commit()

    async def stop(self) -> None:
        for task in self.request_tasks:
            task.cancel()
        self.request_tasks.clear()

    async def start(self, db: AsyncSession, endpoint: Endpoint) -> None:
        clients_set = {
            *await clients_service.get_clients_by_tags(db, self.mailing.clients_tags),
            *await clients_service.get_clients_by_phone_codes(db, self.mailing.clients_mobile_operator_codes),
        }
        for client in clients_set:
            message = await mailings_service.create_message(db, self.mailing, client)
            self.request_tasks.append(asyncio.create_task(self._send(db, endpoint, message, client)))

    @classmethod
    async def get_sending(cls, mailing: Mailing) -> Sending | None:
        return cls.sendings.get(mailing, None)

