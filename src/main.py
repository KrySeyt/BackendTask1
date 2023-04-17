from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware

from .clients.router import router as clients_router
from .mailings.router import router as mailing_router
from .exceptions import validation_error_handler
from .dependencies import get_db, get_db_stub
from .mailings.dependencies import get_endpoint, get_endpoint_stub
from .mailings.events import mailings_in_db_to_schedule
from .middleware import log_raw_request, add_request_uuid, log_response
from .logging import configure_logging


configure_logging()

app = FastAPI()

app.include_router(mailing_router)
app.include_router(clients_router)

app.add_middleware(BaseHTTPMiddleware, dispatch=log_response)
app.add_middleware(BaseHTTPMiddleware, dispatch=log_raw_request)
app.add_middleware(BaseHTTPMiddleware, dispatch=add_request_uuid)

app.add_exception_handler(RequestValidationError, validation_error_handler)

app.add_event_handler("startup", mailings_in_db_to_schedule)

app.dependency_overrides[get_db_stub] = get_db
app.dependency_overrides[get_endpoint_stub] = get_endpoint
