from __future__ import annotations
import asyncio
from .endpoints import Endpoint

from .schema import Mailing, Message, Client, MessageStatus
from . import crud


EXTERNAL_SERVICE_ENDPOINT = r"https://httpbin.org/post"
MAX_REQUESTS_AT_TIME = 20


class Sending:
    sendings: dict[Mailing, Sending] = dict()
    request_tasks_semaphore = asyncio.Semaphore(MAX_REQUESTS_AT_TIME)

    def __init__(self, mailing: Mailing):
        self.mailing = mailing
        self.sendings[mailing] = self
        self.request_tasks: list[asyncio.Task] = []

    async def _send(self, endpoint: Endpoint, message: Message, client: Client) -> None:
        sleep_time = 0
        status_code = 0
        while status_code < 200 or status_code >= 300:
            async with self.request_tasks_semaphore:
                status_code = await endpoint.send(message, client, self.mailing)
            sleep_time += 20
            await asyncio.sleep(sleep_time)
        message.status = MessageStatus.delivered

    async def stop(self) -> None:
        for task in self.request_tasks:
            task.cancel()

    async def start(self, endpoint: Endpoint) -> None:
        clients = {
            *crud.get_clients_by_tags(self.mailing.clients_tags),
            *crud.get_clients_by_phone_codes(self.mailing.clients_mobile_operator_codes),
        }
        for client in clients:
            message = crud.create_message(self.mailing, client)
            self.request_tasks.append(asyncio.create_task(self._send(endpoint, message, client)))

    @classmethod
    async def get_sending(cls, mailing: Mailing) -> Sending | None:
        return cls.sendings.get(mailing, None)

