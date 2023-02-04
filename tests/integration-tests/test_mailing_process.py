import asyncio
import datetime
import random

import pytz

from app.mailing_service import mailings, schema, endpoints, sending
from app.database import crud


class SemiworkingEndpoint(endpoints.Endpoint):
    def __init__(self):
        self.working = True
        self.sended_messages_count = 0
        self.event = asyncio.Event()

    async def send(self, message: schema.Message,
                   client: schema.Client,
                   mailing: schema.Mailing) -> endpoints.StatusCode:

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

        client = schema.ClientIn(
            tag=schema.MailingTagIn(text="Tag"),
            phone_number=f"+{random.randrange(70000000000, 80000000000)}",
            phone_operator_code=int(phone_number[1:4]),
            timezone=random.choice(pytz.all_timezones)
        )
        mailing_clients.append(client)

    await crud.create_clients(testing_database, mailing_clients)

    mailing = schema.MailingIn(
        text="Mailing text",
        start_time=datetime.datetime.now(),
        end_time=datetime.datetime.now() + datetime.timedelta(seconds=30),
        clients_tags=[schema.MailingTagIn(text="Tag")],
        clients_mobile_operator_codes=[900, 910, 999],
    )
    endpoint = SemiworkingEndpoint()
    mailing = await mailings.create_mailing(testing_database, mailing, endpoint)

    await endpoint.event.wait()
    sending_ = await sending.Sending.get_sending(mailing)
    await asyncio.sleep(0.3)

    await mailings.delete_mailing(testing_database, mailing)
    sended_count = endpoint.sended_messages_count
    await asyncio.sleep(0.5)
    assert endpoint.sended_messages_count == sended_count
    assert len(sending_.request_tasks) == 0
