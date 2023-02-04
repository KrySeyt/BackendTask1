from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database.database import get_sessionmaker
from app.mailing_service.endpoints import Endpoint, APIEndpoint, TestEndpoint


async def get_db() -> AsyncSession:
    if hasattr(get_db, "db"):
        db: AsyncSession = get_db.db
        return db
    sessionmaker = await get_sessionmaker()
    db = sessionmaker()
    setattr(get_db, "db", db)
    return db


async def get_db_stub() -> None:
    raise NotImplementedError


async def get_endpoint() -> Endpoint:
    endpoint_url = get_settings().endpoint_url
    endpoint = APIEndpoint(endpoint_url) if endpoint_url else TestEndpoint()
    return endpoint


async def get_endpoint_stub() -> None:
    raise NotImplementedError
