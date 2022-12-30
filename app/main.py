from collections import Counter, defaultdict
from fastapi import FastAPI, Request, status, Path, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from .schema import ClientIn, ClientOut, ClientInWithID, MailingOut, MailingIn, MailingInWithID, MailingStats, \
    MailingStatsOut, MessageStatus, DetailMailingStatsOut, DetailMailingStats
from . import crud

app = FastAPI()


@app.exception_handler(RequestValidationError)
def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({
            "detail": exc.errors(),
            "body": exc.body,
            "params": {**request.path_params, **request.query_params}
        })
    )


@app.post("/client/",
          response_model=ClientOut,
          tags=["client"])
def create_client(client: ClientIn):
    client = crud.create_client(client)
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
def update_client(client: ClientInWithID):
    db_client = crud.get_client_by_id(client.id)
    if not db_client:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="This client doesn't exists")
    return crud.update_client(client)


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
def get_client(client_id: int = Path()):
    if client_id >= crud.next_client_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Wrong ID")
    client = crud.get_client_by_id(client_id)
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
def delete_client(client_id: int = Path()):
    client = crud.get_client_by_id(client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Client with this ID doesnt exists")
    return crud.delete_client(client_id)


@app.get("/clients/",
         response_model=list[ClientOut],
         tags=["client"])
def get_clients(skip: int = 0, limit: int = 100):
    clients = crud.get_clients(skip, limit)
    return clients


@app.post("/mailing/",
          tags=["mailing"],
          response_model=MailingOut)
def create_mailing(mailing: MailingIn):
    return crud.create_mailing(mailing)


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
def delete_mailing(mailing_id: int = Path()):
    mailing = crud.get_mailing_by_id(mailing_id)
    if not mailing:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Mailing with this ID doesn't exists")
    return crud.delete_mailing(mailing_id)


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
def update_mailing(mailing: MailingInWithID):
    mailing_in_db = crud.get_mailing_by_id(mailing.id)
    if not mailing_in_db:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Mailing with this ID doesn't exists")
    return crud.update_mailing(mailing)


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
def get_mailing(mailing_id: int = Path()):
    mailing = crud.get_mailing_by_id(mailing_id)
    if not mailing:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "Mailing with this ID doesn't exists")
    return mailing


@app.get("/stats/",
         tags=["stats"],
         response_model=list[MailingStatsOut])
def get_stats():
    stats = []
    for mailing in crud.get_all_mailings():
        messages = crud.get_mailing_messages(mailing.id)
        messages = dict(Counter((message.status for message in messages)))
        for sts in MessageStatus:
            if sts not in messages:
                messages[sts] = 0
        stats.append(MailingStats(mailing=mailing, messages=messages))
    return stats


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
def get_one_mailing_stats(mailing_id: int = Path()):
    mailing = crud.get_mailing_by_id(mailing_id)
    if not mailing:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Mailing with this ID doesn't exists")
    messages = crud.get_mailing_messages(mailing_id)
    return DetailMailingStats(mailing=mailing, messages=messages)
