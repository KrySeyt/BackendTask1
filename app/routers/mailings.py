from fastapi import APIRouter, Path, status, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.mailing_service import mailings
from app.mailing_service.endpoints import Endpoint
from app.mailing_service.schema import MailingOut, ValidationErrorSchema, MailingIn, Mailing, MailingInWithID

from ..dependencies import get_db_stub, get_endpoint_stub


router = APIRouter()


@router.post("/mailing/",
             tags=["mailing"],
             response_model=MailingOut,
             responses={422: {"model": ValidationErrorSchema}}
             )
async def create_mailing(mailing: MailingIn,
                         db: AsyncSession = Depends(get_db_stub),
                         endpoint: Endpoint = Depends(get_endpoint_stub)) -> Mailing:
    return await mailings.create_mailing(db, mailing, endpoint)


@router.delete("/mailing/{mailing_id}",
               tags=["mailing"],
               response_model=MailingOut,
               responses={422: {"model": ValidationErrorSchema}, 404: {}}
               )
async def delete_mailing(mailing_id: int = Path(), db: AsyncSession = Depends(get_db_stub)) -> Mailing:
    mailing = await mailings.get_mailing_by_id(db, mailing_id)
    if not mailing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return await mailings.delete_mailing(db, mailing)


@router.put("/mailing/",
            tags=["mailing"],
            response_model=MailingOut,
            responses={422: {"model": ValidationErrorSchema}, 404: {}}
            )
async def update_mailing(mailing: MailingInWithID,
                         db: AsyncSession = Depends(get_db_stub),
                         endpoint: Endpoint = Depends(get_endpoint_stub)) -> Mailing | None:
    mailing_in_db = await mailings.get_mailing_by_id(db, mailing.id)
    if not mailing_in_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return await mailings.update_mailing(db, mailing, endpoint)


@router.get("/mailing/{mailing_id}",
            response_model=MailingOut,
            tags=["mailing"],
            responses={422: {"model": ValidationErrorSchema}, 404: {}}
            )
async def get_mailing(mailing_id: int = Path(), db: AsyncSession = Depends(get_db_stub)) -> Mailing:
    mailing = await mailings.get_mailing_by_id(db, mailing_id)
    if not mailing:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return mailing
