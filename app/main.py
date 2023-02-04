from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from .mailing_service.schedule import Schedule
from .routers import clients, mailings, stats
from .exception_handlers import validation_error_handler
from .mailing_service.mailings import get_all_mailings

from .dependencies import get_db, get_db_stub, get_endpoint, get_endpoint_stub


app = FastAPI()


@app.on_event("startup")
async def mailings_in_db_to_schedule() -> None:
    db = await get_db()
    all_mailings = await get_all_mailings(db)
    for mailing in all_mailings:
        await Schedule.add_mailing_to_schedule(db, mailing, await get_endpoint())


@app.on_event("shutdown")
async def close_db_session() -> None:
    db = await get_db()
    await db.close()


app.include_router(clients.router)
app.include_router(mailings.router)
app.include_router(stats.router)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.dependency_overrides[get_db_stub] = get_db
app.dependency_overrides[get_endpoint_stub] = get_endpoint
