from .dependencies import get_db


async def close_db_session() -> None:
    db = await get_db()
    await db.close()
