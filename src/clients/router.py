from fastapi import APIRouter, status, HTTPException, Path, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.clients import service
from .schema import ClientOut, ClientIn, Client, ClientInWithID
from src.exceptions import ValidationErrorSchema
from src.dependencies import get_db_stub
from src.logging import log_parsed_request


router = APIRouter(dependencies=[Depends(log_parsed_request)])


@router.post(
    "/client/",
    response_model=ClientOut,
    tags=["client"],
    responses={422: {"model": ValidationErrorSchema}}
)
async def create_client(client_in: ClientIn, db: AsyncSession = Depends(get_db_stub)) -> Client:
    client = await service.create_client(db, client_in)
    return client


@router.put(
    "/client/",
    response_model=ClientOut | None,
    tags=["client"],
    responses={422: {"model": ValidationErrorSchema}, 404: {}}
)
async def update_client(client: ClientInWithID, db: AsyncSession = Depends(get_db_stub)) -> Client | None:
    db_client = await service.get_client_by_id(db, client.id)
    if not db_client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return await service.update_client(db, client)


@router.get(
    "/client/{client_id}",
    response_model=ClientOut,
    tags=["client"],
    responses={422: {"model": ValidationErrorSchema}, 404: {}}
)
async def get_client(client_id: int = Path(), db: AsyncSession = Depends(get_db_stub)) -> Client:
    client = await service.get_client_by_id(db, client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return client


@router.delete(
    "/client/{client_id}",
    response_model=ClientOut,
    tags=["client"],
    responses={422: {"model": ValidationErrorSchema}, 404: {}}
)
async def delete_client(client_id: int = Path(), db: AsyncSession = Depends(get_db_stub)) -> Client | None:
    client = await service.get_client_by_id(db, client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return await service.delete_client(db, client_id)


@router.get(
    "/clients/",
    response_model=list[ClientOut],
    tags=["client"],
    responses={422: {"model": ValidationErrorSchema}}
)
async def get_clients(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db_stub)) -> list[Client]:
    clients_list = await service.get_clients(db, skip, limit)
    return clients_list
