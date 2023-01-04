from fastapi import FastAPI, Request, status, Path, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from .schema import ClientIn, ClientOut, ClientInWithID, MailingOut, MailingIn, MailingInWithID, \
    MailingStatsOut, DetailMailingStatsOut, Client, Mailing, MailingStats, DetailMailingStats
from . import mailings, stats
from . import clients
from .database import SessionLocal
from .schedule import Schedule
from .endpoints import APIEndpoint, TestEndpoint

app = FastAPI()


# endpoint = APIEndpoint(r'https://httpbin.org/post/')
endpoint = TestEndpoint()
db_session: AsyncSession = SessionLocal()


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


@app.on_event("shutdown")
async def close_db_session() -> None:
    global db_session
    await db_session.close()


async def get_db() -> AsyncSession:
    global db_session
    return db_session


@app.on_event("startup")
async def mailings_in_db_to_schedule() -> None:
    db = await get_db()
    all_mailings = await mailings.get_all_mailings(db)
    for mailing in all_mailings:
        await Schedule.add_mailing_to_schedule(db, mailing, endpoint)


@app.post("/client/",
          response_model=ClientOut,
          tags=["client"])
async def create_client(client_in: ClientIn, db: AsyncSession = Depends(get_db)) -> Client:
    client = await clients.create_client(db, client_in)
    return client


@app.put("/client/",
         response_model=ClientOut,
         tags=["client"],
         responses={
             422: {
                 "description": "Client with this is doesn't exist",
                 "content": {
                     "application/json": {
                         "example": {"detail": "This client doesn't exists"}
                     }
                 }
             }
         })
async def update_client(client: ClientInWithID, db: AsyncSession = Depends(get_db)) -> Client | None:
    db_client = await clients.get_client_by_id(db, client.id)
    if not db_client:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="This client doesn't exists")
    return await clients.update_client(db, client)


@app.get("/client/{client_id}",
         response_model=ClientOut,
         tags=["client"],
         responses={
             422: {
                 "description": "Wrong ID",
                 "content": {
                     "application/json": {
                         "example": {"detail": "Wrong ID"}
                     }
                 },
             }
         })
async def get_client(client_id: int = Path(), db: AsyncSession = Depends(get_db)) -> Client:
    client = await clients.get_client_by_id(db, client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Wrong ID")
    return client


@app.delete("/client/{client_id}",
            response_model=ClientOut,
            tags=["client"],
            responses={
                422: {
                    "description": "Wrong ID",
                    "content": {
                        "application/json": {
                            "example": {"detail": "Client with this ID doesnt exists"}
                        }
                    },
                }
            })
async def delete_client(client_id: int = Path(), db: AsyncSession = Depends(get_db)) -> Client | None:
    client = await clients.get_client_by_id(db, client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Client with this ID doesnt exists")
    return await clients.delete_client(db, client_id)


@app.get("/clients/",
         response_model=list[ClientOut],
         tags=["client"])
async def get_clients(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)) -> list[Client]:
    clients_list = await clients.get_clients(db, skip, limit)
    return clients_list


@app.post("/mailing/",
          tags=["mailing"],
          response_model=MailingOut)
async def create_mailing(mailing: MailingIn, db: AsyncSession = Depends(get_db)) -> Mailing:
    return await mailings.create_mailing(db, mailing, endpoint)


@app.delete("/mailing/{mailing_id}",
            tags=["mailing"],
            response_model=MailingOut,
            responses={
                422: {
                    "description": "Wrong ID",
                    "content": {
                        "application/json": {
                            "example": {"detail": "Mailing with this ID doesnt exists"}
                        }
                    },
                }
            })
async def delete_mailing(mailing_id: int = Path(), db: AsyncSession = Depends(get_db)) -> Mailing:
    mailing = await mailings.get_mailing_by_id(db, mailing_id)
    if not mailing:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Mailing with this ID doesn't exists")
    return await mailings.delete_mailing(db, mailing)


@app.put("/mailing/",
         tags=["mailing"],
         response_model=MailingOut,
         responses={
             422: {
                 "description": "Wrong ID",
                 "content": {
                     "application/json": {
                         "example": {"detail": "Mailing with this ID doesn't exists"}
                     }
                 },
             }
         })
async def update_mailing(mailing: MailingInWithID, db: AsyncSession = Depends(get_db)) -> Mailing | None:
    mailing_in_db = await mailings.get_mailing_by_id(db, mailing.id)
    if not mailing_in_db:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Mailing with this ID doesn't exists")
    return await mailings.update_mailing(db, mailing, endpoint)


@app.get("/mailing/{mailing_id}",
         response_model=MailingOut,
         tags=["mailing"],
         responses={
             422: {
                 "description": "Wrong ID",
                 "content": {
                     "application/json": {
                         "example": {"detail": "Mailing with this ID doesn't exists"}
                     }
                 },
             }
         })
async def get_mailing(mailing_id: int = Path(), db: AsyncSession = Depends(get_db)) -> Mailing:
    mailing = await mailings.get_mailing_by_id(db, mailing_id)
    if not mailing:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "Mailing with this ID doesn't exists")
    return mailing


@app.get("/stats/",
         tags=["stats"],
         response_model=list[MailingStatsOut])
async def get_stats(db: AsyncSession = Depends(get_db)) -> list[MailingStats]:
    return await stats.get_stats(db)


@app.get("/stats/{mailing_id}",
         tags=["stats"],
         response_model=DetailMailingStatsOut,
         responses={
             422: {
                 "description": "Wrong ID",
                 "content": {
                     "application/json": {
                         "example": {"detail": "Mailing with this ID desn't exists"}
                     }
                 },
             }
         })
async def get_mailing_stats(mailing_id: int = Path(), db: AsyncSession = Depends(get_db)) -> DetailMailingStats | None:
    mailing = await mailings.get_mailing_by_id(db, mailing_id)
    if not mailing:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Mailing with this ID doesn't exists")
    return await stats.get_mailing_stats(db, mailing)
