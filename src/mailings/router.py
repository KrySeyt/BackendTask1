from fastapi import APIRouter, Path, status, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.mailings import service
from src.mailings.endpoints import Endpoint
from src.mailings.schema import MailingOut, MailingIn, Mailing, MailingInWithID, \
    DetailMailingStats, DetailMailingStatsOut, MailingStats, MailingStatsOut
from src.exceptions import ValidationErrorSchema
from src.dependencies import get_db_stub, log_parsed_request

from .dependencies import get_endpoint_stub


router = APIRouter(dependencies=[Depends(log_parsed_request)])


@router.post("/mailing/",
             tags=["mailing"],
             response_model=MailingOut,
             responses={422: {"model": ValidationErrorSchema}}
             )
async def create_mailing(mailing: MailingIn,
                         db: AsyncSession = Depends(get_db_stub),
                         endpoint: Endpoint = Depends(get_endpoint_stub)) -> Mailing:
    return await service.create_mailing(db, mailing, endpoint)


@router.delete("/mailing/{mailing_id}",
               tags=["mailing"],
               response_model=MailingOut,
               responses={422: {"model": ValidationErrorSchema}, 404: {}}
               )
async def delete_mailing(mailing_id: int = Path(), db: AsyncSession = Depends(get_db_stub)) -> Mailing:
    mailing = await service.get_mailing_by_id(db, mailing_id)
    if not mailing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return await service.delete_mailing(db, mailing)


@router.put("/mailing/",
            tags=["mailing"],
            response_model=MailingOut,
            responses={422: {"model": ValidationErrorSchema}, 404: {}}
            )
async def update_mailing(mailing: MailingInWithID,
                         db: AsyncSession = Depends(get_db_stub),
                         endpoint: Endpoint = Depends(get_endpoint_stub)) -> Mailing | None:
    mailing_in_db = await service.get_mailing_by_id(db, mailing.id)
    if not mailing_in_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return await service.update_mailing(db, mailing, endpoint)


@router.get("/mailing/{mailing_id}",
            response_model=MailingOut,
            tags=["mailing"],
            responses={422: {"model": ValidationErrorSchema}, 404: {}}
            )
async def get_mailing(mailing_id: int = Path(), db: AsyncSession = Depends(get_db_stub)) -> Mailing:
    mailing = await service.get_mailing_by_id(db, mailing_id)
    if not mailing:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return mailing


@router.get("/stats/",
            tags=["stats"],
            response_model=list[MailingStatsOut],
            )
async def get_stats(db: AsyncSession = Depends(get_db_stub)) -> list[MailingStats]:
    return await service.get_stats(db)


@router.get("/stats/{mailing_id}",
            tags=["stats"],
            response_model=DetailMailingStatsOut,
            responses={422: {"model": ValidationErrorSchema}, 404: {}}
            )
async def get_mailing_stats(mailing_id: int = Path(),
                            db: AsyncSession = Depends(get_db_stub)) -> DetailMailingStats | None:
    mailing = await service.get_mailing_by_id(db, mailing_id)
    if not mailing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return await service.get_mailing_stats(db, mailing)
