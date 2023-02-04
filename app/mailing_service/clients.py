from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.mailing_service import schema
from app.database import crud


async def create_client(db: AsyncSession, client: schema.ClientIn) -> schema.Client:
    return schema.Client.from_orm(await crud.create_client(db, client))


async def get_client_by_id(db: AsyncSession, client_id: int) -> schema.Client | None:
    db_client = await crud.get_client_by_id(db, client_id)
    if not db_client:
        return None
    return schema.Client.from_orm(db_client)


async def get_client_by_phone_number(db: AsyncSession, phone_number: int) -> schema.Client | None:
    db_client = await crud.get_client_by_phone_number(db, phone_number)
    if not db_client:
        return None
    return schema.Client.from_orm(db_client)


async def get_clients(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[schema.Client]:
    return list(map(schema.Client.from_orm, await crud.get_clients(db, skip, limit)))


async def update_client(db: AsyncSession, client: schema.ClientInWithID) -> schema.Client | None:
    updated_db_client = await crud.update_client(db, client)
    if not updated_db_client:
        return None
    return schema.Client.from_orm(updated_db_client)


async def delete_client(db: AsyncSession, client_id: int) -> schema.Client | None:
    db_client = await crud.delete_client(db, client_id)
    if not db_client:
        return None
    return schema.Client.from_orm(db_client)


async def get_clients_by_tag(db: AsyncSession, tag: schema.MailingTag) -> list[schema.Client]:
    return list(map(schema.Client.from_orm, await crud.get_clients_by_tag(db, tag)))


async def get_clients_by_tags(db: AsyncSession, tags: list[schema.MailingTag]) -> list[schema.Client]:
    return list(map(schema.Client.from_orm, await crud.get_clients_by_tags(db, tags)))


async def get_clients_by_phone_code(db: AsyncSession, phone_code: int) -> list[schema.Client]:
    return list(map(schema.Client.from_orm, await crud.get_clients_by_phone_code(db, phone_code)))


async def get_clients_by_phone_codes(db: AsyncSession, phone_codes: Sequence[int]) -> list[schema.Client]:
    return list(map(schema.Client.from_orm, await crud.get_clients_by_phone_codes(db, phone_codes)))
