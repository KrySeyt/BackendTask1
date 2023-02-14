from typing import Awaitable, Callable
from uuid import uuid4

from fastapi import Request, Response
from loguru import logger

from . import context


async def add_request_uuid(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    uuid = uuid4()
    context.request_uuid.set(uuid)
    return await call_next(request)


async def log_raw_request(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    request_uuid = context.request_uuid.get()
    logger.bind(
        api_received_request=True,
        request_uuid=request_uuid.hex if request_uuid else None,
        request_method=request.method,
        request_method_version=request["http_version"],
        request_type=request["type"].upper(),
        client_host=request.client.host if request.client else None,
        client_port=request.client.port if request.client else None,
    ).info("API Request received")

    return await call_next(request)


async def log_response(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    response: Response = await call_next(request)
    request_uuid = context.request_uuid.get()
    logger.bind(
        api_sent_response=True,
        request_uuid=request_uuid.hex if request_uuid else None,
        status_code=response.status_code,
        content_type=response.headers.get("content-type"),
    ).info("API Response sent")
    return response
