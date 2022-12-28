from fastapi import FastAPI, Request, status, Path, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from .schema import ClientIn, ClientOut
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


@app.post("/client/", response_model=ClientOut)
def create_client(client: ClientIn):
    client = crud.create_client(client)
    return client


@app.get("/client/{client_id}", response_model=ClientOut, responses={
    422: {
        "description": "Wrong ID",
        "content": {
            "application/json": {
                "example": {"message": "Wrong ID"}
            }
        },
    }
})
def get_client(client_id: int = Path()):
    if client_id >= crud.next_client_id:
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"message": "Wrong ID"})
    client = crud.get_client_by_id(client_id)
    return client


@app.get("/clients/", response_model=list[ClientOut])
def get_clients(skip: int = 0, limit: int = 100):
    clients = crud.get_clients(skip, limit)
    return clients


@app.post("/mailing/")
def create_mailing():
    pass


@app.get("/mailings/")
def get_mailings(skip: int = 0, limit: int = 100):
    pass


@app.get('/stats/')
def get_stats():
    pass
