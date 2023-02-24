import sys
import logging

from loguru import logger

from .config import get_settings


def add_api_parsed_request_log_handling() -> None:
    logger.add(
        sys.stdout,
        level="INFO",
        format=get_settings().logging.format +
        " | API parsed   request | {extra[request_uuid]}"
        " | {extra[source_file]}.{extra[source_function]}"
        " | <level>{message}</level>"
        "\nPath: {extra[request_path_params]}"
        "\nQuery: {extra[request_query_params]}"
        "\nBody: {extra[request_body_params]}",
        enqueue=True,
        filter=lambda record: "api_parsed_request" in record["extra"]
    )


def add_api_received_request_log_handling() -> None:
    logger.add(
        sys.stdout,
        level="INFO",
        format=get_settings().logging.format +
        " | API received request | {extra[request_uuid]}"
        " | {extra[request_type]:<6} {extra[request_method_version]}"
        " | {extra[request_method]:<8} | {extra[client_host]}:{extra[client_port]}"
        " | <level>{message}</level>",
        enqueue=True,
        filter=lambda record: "api_received_request" in record["extra"]
    )


def add_api_response_log_handling() -> None:
    logger.add(
        sys.stdout,
        level="INFO",
        format=get_settings().logging.format +
        " | API sent response | {extra[request_uuid]} | {extra[status_code]}"
        " | Content-type: {extra[content_type]} | <level>{message}</level>",
        enqueue=True,
        filter=lambda record: "api_sent_response" in record["extra"]
    )


# def add_message_sending_log_handling() -> None:
#     logger.add(
#         sys.stdout,
#         level="INFO",
#         format=get_settings().logging.format +
#         " | Message sending | {extra[sending_status]:<7} | {extra[status_code]}"
#         " | <level>{message}</level>",
#         enqueue=True,
#         filter=lambda record: "message_sent" in record["extra"]
#     )


def stop_uvicorn_logging() -> None:
    logging.getLogger("uvicorn.access").handlers = []


def remove_default_loguru_handler() -> None:
    logger.remove(0)


def configure_logging() -> None:
    stop_uvicorn_logging()
    remove_default_loguru_handler()

    add_api_received_request_log_handling()
    add_api_parsed_request_log_handling()
    add_api_response_log_handling()
    # add_message_sending_log_handling()
