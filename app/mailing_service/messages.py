from sqlalchemy.ext.asyncio import AsyncSession

from app.mailing_service import schema
from app.database import crud


async def create_message(db: AsyncSession, mailing: schema.Mailing, client: schema.Client) -> schema.Message:
    return schema.Message.from_orm(await crud.create_message(db, mailing, client))
