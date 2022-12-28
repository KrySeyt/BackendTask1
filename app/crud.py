from .schema import Client, ClientIn, ClientOut, Mailing, Message

MAILINGS: list[Mailing] = []  # This is a temporary storage for this, while I didn't implement SqlAlchemy + Alembic

CLIENTS: list[Client] = []  # And this
next_client_id = 0

MESSAGES: list[Message] = []  # And this


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
    raise ValueError("Client with this ID doesn't exist")


def get_clients(skip: int = 0, limit: int = 100) -> list[Client]:
    return CLIENTS[skip:limit]
