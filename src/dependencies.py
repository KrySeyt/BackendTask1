from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.database import get_sessionmaker
from src import context


async def get_db() -> AsyncSession:
    if hasattr(get_db, "db"):
        db: AsyncSession = get_db.db
        return db
    sessionmaker = await get_sessionmaker()
    db = sessionmaker()
    setattr(get_db, "db", db)
    return db


async def get_db_stub() -> None:
    raise NotImplementedError


async def log_parsed_request(request: Request) -> None:
    request_body = None

    match request.headers.get("content-type"):
        case "application/json":
            request_body = await request.json()

        case "application/x-www-form-urlencoded":
            request_body = await request.form()

    if not request_body:
        request_body = {}

    uuid = context.request_uuid.get()

    logger.bind(
        api_parsed_request=True,
        source_function=request["endpoint"].__name__,
        source_file=request["endpoint"].__module__,
        request_uuid=uuid.hex if uuid else None,
        request_path_params=request.path_params,
        request_query_params=request.query_params,
        request_body_params=request_body,
    ).info("API request processed")
