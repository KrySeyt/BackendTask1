from sqlalchemy.ext.asyncio import AsyncSession

from . import schema, crud


async def create_message(db: AsyncSession, mailing: schema.Mailing, client: schema.Client) -> schema.Message:
    return schema.Message.from_orm(await crud.create_message(db, mailing, client))
