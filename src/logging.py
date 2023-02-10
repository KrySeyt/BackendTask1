import sys


from loguru import logger
from fastapi import Request

from . import context
from .config import get_settings


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
        source_function=request["endpoint"].__name__,
        source_file=request["endpoint"].__module__,
        request_status="Processed",
        request_uuid=uuid.hex if uuid else None,
        request_path_params=request.path_params,
        request_query_params=request.query_params,
        request_body_params=request_body,
    ).info("Processed successful")


def add_parsed_request_log_handling() -> None:
    logger.add(
        sys.stdout,
        level="INFO",
        format=get_settings().logging.format +
        " | {extra[request_status]:<10} request | {extra[request_uuid]}"
        " | {extra[source_file]}.{extra[source_function]}"
        " | <level>{message}</level>"
        "\nPath: {extra[request_path_params]}"
        "\nQuery: {extra[request_query_params]}"
        "\nBody: {extra[request_body_params]}",
        enqueue=True,
        filter=lambda record: record["extra"].get("request_status") == "Processed"
    )


def add_received_request_log_handling() -> None:
    logger.add(
        sys.stdout,
        level="INFO",
        format=get_settings().logging.format +
        " | {extra[request_status]:<10} request | {extra[request_uuid]}"
        " | {extra[request_type]:<6} {extra[request_method_version]}"
        " | {extra[request_method]:<8} | {extra[client_host]}:{extra[client_port]}"
        " | <level>{message}</level>",
        enqueue=True,
        filter=lambda record: record["extra"].get("request_status") == "Incoming"
    )


def add_response_log_handling() -> None:
    logger.add(
        sys.stdout,
        level="INFO",
        format=get_settings().logging.format +
        " | Sending response | {extra[request_uuid]} | {extra[status_code]}"
        " | Content-type: {extra[content_type]} | <level>{message}</level>",
        enqueue=True,
        filter=lambda record: bool(record["extra"].get("response"))
    )


def configure_logging() -> None:
    logger.remove(0)
    add_received_request_log_handling()
    add_parsed_request_log_handling()
    add_response_log_handling()
