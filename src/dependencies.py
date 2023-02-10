from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_sessionmaker


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
