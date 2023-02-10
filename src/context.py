from contextvars import ContextVar
from uuid import UUID


request_uuid: ContextVar[UUID | None] = ContextVar("reqeust_uuid", default=None)
