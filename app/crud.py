from .schema import Client, ClientIn, Mailing, Message, ClientInWithID, MailingIn, MailingTag, MailingMobileOperatorCode

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


def update_client(client: ClientInWithID) -> Client:
    client_in_list = get_client_by_id(client.id)
    for key in client.dict():
        setattr(client_in_list, key, client.dict()[key])
    return client_in_list


def delete_client(client_id: int) -> Client:
    client_in_list = get_client_by_id(client_id)
    if client_in_list:
        CLIENTS.remove(client_in_list)
    return client_in_list


def create_mailing(mailing: MailingIn) -> Mailing:
    mailing_in_list = Mailing(**mailing.dict(), id=next_mailing_id)

    tags = []
    for tag in mailing.clients_tags:
        db_tag = MailingTag(**tag.dict(), mailing=mailing_in_list, mailing_id=mailing_in_list.id)
        tags.append(db_tag)
    mailing_in_list.clients_tags = tags

    mobile_codes = []
    for code in mailing.clients_mobile_operator_codes:
        db_code = MailingMobileOperatorCode(**code.dict(), mailing=mailing_in_list, mailing_id=mailing_in_list.id)
        mobile_codes.append(db_code)
    mailing_in_list.clients_mobile_operator_codes = mobile_codes

    MAILINGS.append(mailing_in_list)
    return mailing_in_list

