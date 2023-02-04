from .mailing_service.schedule import Schedule
from .mailing_service.mailings import get_all_mailings
from .dependencies import get_db, get_endpoint


async def mailings_in_db_to_schedule() -> None:
    db = await get_db()
    all_mailings = await get_all_mailings(db)
    for mailing in all_mailings:
        await Schedule.add_mailing_to_schedule(db, mailing, await get_endpoint())


async def close_db_session() -> None:
    db = await get_db()
    await db.close()
