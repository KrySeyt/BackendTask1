from fastapi import FastAPI, Request, status, Path, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from .schema import ClientIn, ClientOut, ClientInWithID, MailingOut, MailingIn, MailingInWithID, \
    MailingStatsOut, DetailMailingStatsOut, Client, Mailing, MailingStats, DetailMailingStats, ValidationErrorSchema
from . import mailings, stats
from . import clients
from .config import get_settings
from .database import get_sessionmaker
from .schedule import Schedule
from .endpoints import APIEndpoint, TestEndpoint, Endpoint

app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({
            "detail": exc.errors(),
            "body": exc.body,
            "params": {**request.path_params, **request.query_params}
        })
    )


async def get_db() -> AsyncSession:
    if hasattr(get_db, "db"):
        db: AsyncSession = get_db.db
        return db
    sessionmaker = await get_sessionmaker()
    db = sessionmaker()
    setattr(get_db, "db", db)
    return db


@app.on_event("shutdown")
async def close_db_session() -> None:
    db = await get_db()
    await db.close()


async def get_endpoint() -> Endpoint:
    endpoint_url = get_settings().endpoint_url
    endpoint = APIEndpoint(endpoint_url) if endpoint_url else TestEndpoint()
    return endpoint


@app.on_event("startup")
async def mailings_in_db_to_schedule() -> None:
    db = await get_db()
    all_mailings = await mailings.get_all_mailings(db)
    for mailing in all_mailings:
        await Schedule.add_mailing_to_schedule(db, mailing, await get_endpoint())


@app.post("/client/",
          response_model=ClientOut,
          tags=["client"],
          responses={422: {"model": ValidationErrorSchema}}
          )
async def create_client(client_in: ClientIn, db: AsyncSession = Depends(get_db)) -> Client:
    client = await clients.create_client(db, client_in)
    return client


@app.put("/client/",
         response_model=ClientOut | None,
         tags=["client"],
         responses={422: {"model": ValidationErrorSchema}, 404: {}}
         )
async def update_client(client: ClientInWithID, db: AsyncSession = Depends(get_db)) -> Client | None:
    db_client = await clients.get_client_by_id(db, client.id)
    if not db_client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return await clients.update_client(db, client)


@app.get("/client/{client_id}",
         response_model=ClientOut,
         tags=["client"],
         responses={422: {"model": ValidationErrorSchema}, 404: {}}
         )
async def get_client(client_id: int = Path(), db: AsyncSession = Depends(get_db)) -> Client:
    client = await clients.get_client_by_id(db, client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return client


@app.delete("/client/{client_id}",
            response_model=ClientOut,
            tags=["client"],
            responses={422: {"model": ValidationErrorSchema}, 404: {}}
            )
async def delete_client(client_id: int = Path(), db: AsyncSession = Depends(get_db)) -> Client | None:
    client = await clients.get_client_by_id(db, client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return await clients.delete_client(db, client_id)


@app.get("/clients/",
         response_model=list[ClientOut],
         tags=["client"],
         responses={422: {"model": ValidationErrorSchema}}
         )
async def get_clients(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)) -> list[Client]:
    clients_list = await clients.get_clients(db, skip, limit)
    return clients_list


@app.post("/mailing/",
          tags=["mailing"],
          response_model=MailingOut,
          responses={422: {"model": ValidationErrorSchema}}
          )
async def create_mailing(mailing: MailingIn,
                         db: AsyncSession = Depends(get_db),
                         endpoint: Endpoint = Depends(get_endpoint)) -> Mailing:
    return await mailings.create_mailing(db, mailing, endpoint)


@app.delete("/mailing/{mailing_id}",
            tags=["mailing"],
            response_model=MailingOut,
            responses={422: {"model": ValidationErrorSchema}, 404: {}}
            )
async def delete_mailing(mailing_id: int = Path(), db: AsyncSession = Depends(get_db)) -> Mailing:
    mailing = await mailings.get_mailing_by_id(db, mailing_id)
    if not mailing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return await mailings.delete_mailing(db, mailing)


@app.put("/mailing/",
         tags=["mailing"],
         response_model=MailingOut,
         responses={422: {"model": ValidationErrorSchema}, 404: {}}
         )
async def update_mailing(mailing: MailingInWithID,
                         db: AsyncSession = Depends(get_db),
                         endpoint: Endpoint = Depends(get_endpoint)) -> Mailing | None:
    mailing_in_db = await mailings.get_mailing_by_id(db, mailing.id)
    if not mailing_in_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return await mailings.update_mailing(db, mailing, endpoint)


@app.get("/mailing/{mailing_id}",
         response_model=MailingOut,
         tags=["mailing"],
         responses={422: {"model": ValidationErrorSchema}, 404: {}}
         )
async def get_mailing(mailing_id: int = Path(), db: AsyncSession = Depends(get_db)) -> Mailing:
    mailing = await mailings.get_mailing_by_id(db, mailing_id)
    if not mailing:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return mailing


@app.get("/stats/",
         tags=["stats"],
         response_model=list[MailingStatsOut],
         )
async def get_stats(db: AsyncSession = Depends(get_db)) -> list[MailingStats]:
    return await stats.get_stats(db)


@app.get("/stats/{mailing_id}",
         tags=["stats"],
         response_model=DetailMailingStatsOut,
         responses={422: {"model": ValidationErrorSchema}, 404: {}}
         )
async def get_mailing_stats(mailing_id: int = Path(), db: AsyncSession = Depends(get_db)) -> DetailMailingStats | None:
    mailing = await mailings.get_mailing_by_id(db, mailing_id)
    if not mailing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return await stats.get_mailing_stats(db, mailing)
