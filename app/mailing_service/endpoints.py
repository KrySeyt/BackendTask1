from abc import ABC, abstractmethod

import aiohttp

from app.mailing_service.schema import Message, Client, Mailing


StatusCode = int


class Endpoint(ABC):
    @abstractmethod
    async def send(self, message: Message, client: Client, mailing: Mailing) -> StatusCode:
        raise NotImplementedError


class APIEndpoint(Endpoint):
    def __init__(self, endpoint_url: str):
        self.url = endpoint_url if endpoint_url[-1] != '/' else endpoint_url[:-1]
        self.url = endpoint_url

    async def send(self, message: Message, client: Client, mailing: Mailing) -> StatusCode:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.url}/send/{message.id}", json={
                "id": message.id,
                "phone": int(client.phone_number),
                "text": mailing.text,
            }) as response:
                return response.status


class TestEndpoint(Endpoint):
    async def send(self, message: Message, client: Client, mailing: Mailing) -> StatusCode:
        print(f'Message id: {message.id}')
        print(f'Client id: {client.id}')
        print(f'Mailing id: {mailing.id}')
        return 200
