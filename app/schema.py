from __future__ import annotations
from datetime import datetime
from pytz import all_timezones_set
from enum import Enum
from pydantic import BaseModel, Field, validator


class Mailing(BaseModel):
    id: int
    text: str
    clients_tags: list[MailingTags] = []
    clients_mobile_operator_code: list[MailingMobileOperatorCode] = []
    start_time: datetime
    end_time: datetime


class MailingTags(BaseModel):
    id: int
    text: str
    mailing_id: int
    mailing: Mailing


class MailingMobileOperatorCode(BaseModel):
    id: int
    code: int
    mailing_id: int
    mailing: Mailing


class ClientBase(BaseModel):
    phone_number: int = Field(ge=70000000000, le=79999999999)
    phone_operator_code: int
    tag: str | None = None
    timezone: str

    class Config:
        schema_extra = {
            "example": {
                "phone_number": 79009999999,
                "phone_operator_code": 900,
                "tag": "sometag",
                "timezone": "Europe/Amsterdam",
            }
        }

    @validator("timezone")
    def timezone_exists(cls, timezone):
        if timezone not in all_timezones_set:
            raise ValueError("Timezone doesnt exist")
        return timezone


class Client(ClientBase):
    id: int


class ClientIn(ClientBase):
    pass


class ClientOut(ClientBase):
    id: int


class MessageStatus(Enum):
    delivered = "delivered"
    not_delivered = "not delivered"


class Message(BaseModel):
    id: int
    created_at: datetime
    status: MessageStatus
    mailing_id: int
    client_id: int
