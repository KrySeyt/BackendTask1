from abc import ABC, abstractmethod
from http import HTTPStatus

import aiohttp

from src.mailings import schema as mailings_schema
from src.clients import schema as clients_schema


class Endpoint(ABC):
    @abstractmethod
    async def send(self, message: mailings_schema.Message,
                   client: clients_schema.Client,
                   mailing: mailings_schema.Mailing) -> HTTPStatus:
        raise NotImplementedError


class APIEndpoint(Endpoint):
    def __init__(self, endpoint_url: str):
        self.url = endpoint_url if endpoint_url[-1] != '/' else endpoint_url[:-1]
        self.url = endpoint_url

    async def send(self, message: mailings_schema.Message,
                   client: clients_schema.Client,
                   mailing: mailings_schema.Mailing) -> HTTPStatus:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.url}/{message.id}", json={
                "id": message.id,
                "phone": int(client.phone_number),
                "text": mailing.text,
            }) as response:
                return HTTPStatus(response.status)


class TestEndpoint(Endpoint):
    async def send(self, message: mailings_schema.Message,
                   client: clients_schema.Client,
                   mailing: mailings_schema.Mailing) -> HTTPStatus:
        print(f'Message id: {message.id}')
        print(f'Client id: {client.id}')
        print(f'Mailing id: {mailing.id}')
        return HTTPStatus(200)
