from abc import ABC, abstractmethod

from fastapi import status
import aiohttp

from app.schema import Message, Client, Mailing


class Endpoint(ABC):
    @abstractmethod
    async def send(self, message: Message, client: Client, mailing: Mailing) -> int:
        raise NotImplementedError


class APIEndpoint(Endpoint):
    def __init__(self, endpoint_url: str):
        self.url = endpoint_url

    async def send(self, message: Message, client: Client, mailing: Mailing) -> int:
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url) as response:
                return response.status


class TestEndpoint(Endpoint):
    async def send(self, message: Message, client: Client, mailing: Mailing) -> int:
        print(f'Message id: {message.id}')
        print(f'Client id: {client.id}')
        print(f'Mailing id: {mailing.id}')
        return 200
