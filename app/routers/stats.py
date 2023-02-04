from fastapi import APIRouter, HTTPException, Path, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.mailing_service import stats, mailings
from app.mailing_service.schema import MailingStatsOut, MailingStats, DetailMailingStatsOut, ValidationErrorSchema, \
    DetailMailingStats

from ..dependencies import get_db_stub


router = APIRouter()


@router.get("/stats/",
            tags=["stats"],
            response_model=list[MailingStatsOut],
            )
async def get_stats(db: AsyncSession = Depends(get_db_stub)) -> list[MailingStats]:
    return await stats.get_stats(db)


@router.get("/stats/{mailing_id}",
            tags=["stats"],
            response_model=DetailMailingStatsOut,
            responses={422: {"model": ValidationErrorSchema}, 404: {}}
            )
async def get_mailing_stats(mailing_id: int = Path(), db: AsyncSession = Depends(get_db_stub)) -> DetailMailingStats | None:
    mailing = await mailings.get_mailing_by_id(db, mailing_id)
    if not mailing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return await stats.get_mailing_stats(db, mailing)
