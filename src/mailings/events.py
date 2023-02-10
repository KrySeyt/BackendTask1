from src.dependencies import get_db
from src.mailings.dependencies import get_endpoint
from src.mailings.schedule import Schedule
from src.mailings.service import get_all_mailings


async def mailings_in_db_to_schedule() -> None:
    db = await get_db()
    all_mailings = await get_all_mailings(db)
    for mailing in all_mailings:
        await Schedule.add_mailing_to_schedule(db, mailing, await get_endpoint())
