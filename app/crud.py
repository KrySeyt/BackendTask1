from .schema import Client, ClientIn, Mailing, Message, ClientInWithID, MailingIn, MailingTag, \
    MailingMobileOperatorCode, MailingInWithID, MailingStats

MAILINGS: list[Mailing] = []  # This is a temporary storage for this, while I didn't implement SqlAlchemy + Alembic
next_mailing_id = 0

CLIENTS: list[Client] = []  # And this
next_client_id = 0

MESSAGES: list[Message] = []  # And this
next_message_id = 0


def create_client(client: ClientIn) -> Client:
    global next_client_id
    client = Client(**client.dict(), id=next_client_id)
    next_client_id += 1
    CLIENTS.append(client)
    return client


def get_client_by_id(client_id: int) -> Client | None:
    for client in CLIENTS:
        if client.id == client_id:
            return client
    return None


def get_client_by_phone_number(phone_number: int) -> Client | None:
    for client in CLIENTS:
        if client.phone_number == phone_number:
            return client
    return None


def get_clients(skip: int = 0, limit: int = 100) -> list[Client]:
    return CLIENTS[skip:limit]


def update_client(client: ClientInWithID) -> Client | None:
    client_in_list = get_client_by_id(client.id)
    if not client_in_list:
        return None
    for key in client.dict():
        setattr(client_in_list, key, client.dict()[key])
    return client_in_list


def delete_client(client_id: int) -> Client | None:
    client_in_list = get_client_by_id(client_id)
    if client_in_list:
        CLIENTS.remove(client_in_list)
    return client_in_list


def create_mailing(mailing: MailingIn) -> Mailing:
    global next_mailing_id
    mailing_in_list = Mailing(
        text=mailing.text,
        start_time=mailing.start_time,
        end_time=mailing.end_time,
        id=next_mailing_id,
        clients_tags=[MailingTag(**tag.dict()) for tag in mailing.clients_tags],
        clients_mobile_operator_codes=[
            MailingMobileOperatorCode(**code.dict())
            for code in mailing.clients_mobile_operator_codes
        ]
    )

    MAILINGS.append(mailing_in_list)
    next_mailing_id += 1
    return mailing_in_list


def get_mailing_by_id(mailing_id: int) -> Mailing | None:
    for mailing in MAILINGS:
        if mailing.id == mailing_id:
            return mailing
    return None


def delete_mailing(mailing_id: int) -> Mailing | None:
    mailing = get_mailing_by_id(mailing_id)
    if mailing:
        MAILINGS.remove(mailing)
    return mailing


def update_mailing(mailing: MailingInWithID) -> Mailing | None:
    mailing_in_list = get_mailing_by_id(mailing.id)
    if not mailing_in_list:
        return None
    for key in mailing.dict():
        setattr(mailing_in_list, key, mailing.dict()[key])
    return mailing_in_list


def get_all_mailings() -> list[Mailing]:
    return MAILINGS[:]


def get_mailing_messages(mailing_id) -> list[Message]:
    return list(filter(lambda x: x.mailing_id == mailing_id, MESSAGES))
