from contextvars import ContextVar
from uuid import UUID


request_uuid: ContextVar[UUID | None] = ContextVar("request_uuid", default=None)
