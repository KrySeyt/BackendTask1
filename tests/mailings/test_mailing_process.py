import asyncio
import datetime
import random

import pytz

from src.mailings import sending, endpoints
from src.clients import schema as clients_schema
from src.mailings import schema as mailings_schema
from src.mailings import service as mailings_service
from src.clients import crud as clients_crud


class SemiworkingEndpoint(endpoints.Endpoint):
    def __init__(self):
        self.working = True
        self.sended_messages_count = 0
        self.event = asyncio.Event()

    async def send(self, message: mailings_schema.Message,
                   client: clients_schema.Client,
                   mailing: mailings_schema.Mailing) -> endpoints.StatusCode:

        self.event.set()
        try:
            if self.working:
                self.sended_messages_count += 1
                return 200
            else:
                await asyncio.sleep(0.5)
                return 500
        finally:
            self.working = not self.working


async def test_mailing_process(testing_database):
    mailing_clients = []
    for _ in range(1000):
        phone_number = f"+{random.randrange(70000000000, 80000000000)}"

        client = clients_schema.ClientIn(
            tag=mailings_schema.MailingTagIn(text="Tag"),
            phone_number=f"+{random.randrange(70000000000, 80000000000)}",
            phone_operator_code=int(phone_number[1:4]),
            timezone=random.choice(pytz.all_timezones)
        )
        mailing_clients.append(client)

    await clients_crud.create_clients(testing_database, mailing_clients)

    mailing = mailings_schema.MailingIn(
        text="Mailing text",
        start_time=datetime.datetime.now(),
        end_time=datetime.datetime.now() + datetime.timedelta(seconds=30),
        clients_tags=[mailings_schema.MailingTagIn(text="Tag")],
        clients_mobile_operator_codes=[900, 910, 999],
    )
    endpoint = SemiworkingEndpoint()
    mailing = await mailings_service.create_mailing(testing_database, mailing, endpoint)

    await endpoint.event.wait()
    sending_ = await sending.Sending.get_sending(mailing)
    await asyncio.sleep(0.3)

    await mailings_service.delete_mailing(testing_database, mailing)
    sended_count = endpoint.sended_messages_count
    await asyncio.sleep(0.5)
    assert endpoint.sended_messages_count == sended_count
    assert len(sending_.request_tasks) == 0
