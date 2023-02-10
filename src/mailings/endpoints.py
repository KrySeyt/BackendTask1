from abc import ABC, abstractmethod

import aiohttp

from src.mailings import schema as mailings_schema
from src.clients import schema as clients_schema


StatusCode = int


class Endpoint(ABC):
    @abstractmethod
    async def send(self, message: mailings_schema.Message,
                   client: clients_schema.Client,
                   mailing: mailings_schema.Mailing) -> StatusCode:
        raise NotImplementedError


class APIEndpoint(Endpoint):
    def __init__(self, endpoint_url: str):
        self.url = endpoint_url if endpoint_url[-1] != '/' else endpoint_url[:-1]
        self.url = endpoint_url

    async def send(self, message: mailings_schema.Message,
                   client: clients_schema.Client,
                   mailing: mailings_schema.Mailing) -> StatusCode:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.url}/send/{message.id}", json={
                "id": message.id,
                "phone": int(client.phone_number),
                "text": mailing.text,
            }) as response:
                return response.status


class TestEndpoint(Endpoint):
    async def send(self, message: mailings_schema.Message,
                   client: clients_schema.Client,
                   mailing: mailings_schema.Mailing) -> StatusCode:
        print(f'Message id: {message.id}')
        print(f'Client id: {client.id}')
        print(f'Mailing id: {mailing.id}')
        return 200
