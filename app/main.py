from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from .routers import clients, mailings, stats
from .exception_handlers import validation_error_handler
from .dependencies import get_db, get_db_stub, get_endpoint, get_endpoint_stub
from .events import mailings_in_db_to_schedule, close_db_session


app = FastAPI()


app.include_router(clients.router)
app.include_router(mailings.router)
app.include_router(stats.router)

app.add_exception_handler(RequestValidationError, validation_error_handler)

app.add_event_handler("startup", mailings_in_db_to_schedule)
app.add_event_handler("shutdown", close_db_session)

app.dependency_overrides[get_db_stub] = get_db
app.dependency_overrides[get_endpoint_stub] = get_endpoint
