from typing import Iterable

from sqlalchemy_utils import PhoneNumber
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.mailings import crud as mailings_crud
from src.mailings import schema as mailings_schema
from src.mailings.models import MailingTag

from . import models
from . import schema as clients_schema


async def create_client(db: AsyncSession, client: clients_schema.ClientIn) -> models.Client:
    client_tag = await mailings_crud.get_mailing_tag(db, client.tag.text)
    if not client_tag:
        client_tag = MailingTag(**client.tag.dict())

    db_client = models.Client(
        phone_number=client.phone_number,
        phone_operator_code=client.phone_operator_code,
        tag=client_tag,
        timezone=client.timezone
    )

    db.add(db_client)
    await db.commit()
    await db.refresh(db_client)
    return db_client


async def create_clients(db: AsyncSession, clients: Iterable[clients_schema.ClientIn]) -> list[models.Client]:
    db_clients = []
    for client in clients:
        client_tag = await mailings_crud.get_mailing_tag(db, client.tag.text)
        if not client_tag:
            client_tag = await mailings_crud.create_mailing_tag(db, client.tag)

        db_client = models.Client(
            phone_number=client.phone_number,
            phone_operator_code=client.phone_operator_code,
            tag=client_tag,
            timezone=client.timezone
        )
        db_clients.append(db_client)

    db.add_all(db_clients)
    await db.commit()

    for db_client in db_clients:
        await db.refresh(db_client)

    return db_clients


async def get_client_by_id(db: AsyncSession, client_id: int) -> models.Client | None:
    return await db.get(models.Client, client_id)


async def get_client_by_phone_number(db: AsyncSession, phone_number: int) -> models.Client | None:
    return (await db.execute(select(models.Client).filter(
        models.Client.phone_number == phone_number
    ))).scalars().first()


async def get_clients(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[models.Client]:
    return list((await db.execute(select(models.Client).offset(skip).limit(limit))).scalars().all())


async def update_client(db: AsyncSession, client: clients_schema.ClientInWithID) -> models.Client | None:
    db_client = await db.get(models.Client, client.id)
    if not db_client:
        return None
    new_tag = await mailings_crud.get_mailing_tag(db, client.tag.text) or \
              await mailings_crud.create_mailing_tag(db, client.tag)

    db_client.tag_id = new_tag.id
    db_client.tag = new_tag
    db_client.phone_number = PhoneNumber(client.phone_number)
    db_client.phone_operator_code = client.phone_operator_code
    db_client.timezone = client.timezone

    await db.commit()
    await db.refresh(db_client)

    return db_client


async def delete_client(db: AsyncSession, client_id: int) -> models.Client | None:
    db_client = await get_client_by_id(db, client_id)
    if not db_client:
        return None
    await db.delete(db_client)
    await db.commit()
    return db_client


async def get_clients_by_tag(db: AsyncSession, tag: mailings_schema.MailingTag) -> list[models.Client]:
    stmt = select(models.Client).join(MailingTag).filter(MailingTag.id == tag.id)
    return list((await db.execute(stmt)).scalars().all())


async def get_clients_by_tags(db: AsyncSession, tags: list[mailings_schema.MailingTag]) -> list[models.Client]:
    tags_ids = map(lambda x: x.id, tags)
    stmt = select(models.Client).join(MailingTag).where(MailingTag.id.in_(tags_ids))
    return list((await db.scalars(stmt)).all())


async def get_clients_by_phone_code(db: AsyncSession, phone_code: int) -> list[models.Client]:
    return list((await db.execute(select(models.Client).where(
        models.Client.phone_operator_code == phone_code
    ))).scalars().all())


async def get_clients_by_phone_codes(db: AsyncSession, phone_codes: Iterable[int]) -> list[models.Client]:
    return list((await db.execute(select(models.Client).where(
        models.Client.phone_operator_code.in_(set(phone_codes))
    ))).scalars().all())
