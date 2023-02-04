from __future__ import annotations
from datetime import datetime
from typing import Any

from pytz import all_timezones_set
from enum import Enum
from pydantic import BaseModel, validator, Field
from sqlalchemy_utils import PhoneNumber


class HashableBaseModel(BaseModel):
    def __hash__(self) -> int:
        return id(self)


class MailingBase(HashableBaseModel):
    text: str = Field(example="Mailing text")
    start_time: datetime
    end_time: datetime


class Mailing(MailingBase):
    id: int
    clients_tags: list[MailingTag] = []
    clients_mobile_operator_codes: list[int] = []

    class Config:
        orm_mode = True


class MailingIn(MailingBase):
    clients_tags: list[MailingTagIn]
    clients_mobile_operator_codes: list[int] = Field(example=[900, 910])


class MailingInWithID(MailingIn):
    id: int


class MailingOut(MailingBase):
    id: int
    clients_tags: list[MailingTagOut] = []
    clients_mobile_operator_codes: list[int] = Field(example=[900, 910])


class MailingTagBase(BaseModel):
    text: str = Field(example="Any text")


class MailingTag(MailingTagBase):
    id: int

    class Config:
        orm_mode = True


class MailingTagOut(MailingTagBase):
    pass


class MailingTagIn(MailingTagBase):
    pass


class ClientBase(HashableBaseModel):
    phone_number: str = Field(example="+79009999999")
    phone_operator_code: int = Field(example=900)
    timezone: str = Field(example="Europe/Amsterdam")

    @validator("timezone")
    def timezone_exists(cls, timezone: str) -> str:
        if timezone not in all_timezones_set:
            raise ValueError("Timezone doesn't exist")
        return timezone

    @validator("phone_number", pre=True)
    def phone_number_correct(cls, phone_number: str | PhoneNumber) -> str:
        if isinstance(phone_number, PhoneNumber):
            phone_number = phone_number.e164
        if int(phone_number) < 70000000000 or int(phone_number) > 79999999999:
            raise ValueError("Phone number is incorrect")
        return phone_number


class Client(ClientBase):
    id: int
    tag: MailingTag

    class Config:
        orm_mode = True


class ClientIn(ClientBase):
    tag: MailingTagIn


class ClientInWithID(ClientIn):
    id: int = Field(example=0)


class ClientOut(ClientBase):
    id: int = Field(example=0)
    tag: MailingTagOut


class MessageStatus(Enum):
    delivered = "delivered"
    not_delivered = "not delivered"


class Message(BaseModel):
    id: int
    created_at: datetime
    status: MessageStatus
    mailing_id: int
    client_id: int

    class Config:
        orm_mode = True


class MailingStatsBase(BaseModel):
    messages: dict[MessageStatus, int] = Field(
        example={status: 0 for status in MessageStatus}
    )


class MailingStats(MailingStatsBase):
    mailing: Mailing


class MailingStatsOut(MailingStatsBase):
    mailing: MailingOut


class DetailMailingStatsBase(BaseModel):
    messages: list[Message]


class DetailMailingStats(DetailMailingStatsBase):
    mailing: Mailing


class DetailMailingStatsOut(DetailMailingStatsBase):
    mailing: MailingOut


class ValidationErrorSchema(BaseModel):
    detail: list[dict[str, Any]] = Field(description="Default detail of validation error", example=[
        {
            "loc": [
                "body",
                "phone_number"
            ],
            "msg": "field required",
            "type": "value_error.missing",
        }
    ])
    body: dict[str, Any] = Field(description="Body of your request", example={
        "phone_operator_code": 900,
        "timezone": "Europe/Amsterdam",
        "id": 0,
        "tag": {
            "text": "Any text"
        }
    })
    params: dict[str, Any] = Field(description="Path and query parameters of your request", example={
        "deprecated_param": 1
    })


Mailing.update_forward_refs()
MailingIn.update_forward_refs()
MailingOut.update_forward_refs()
MailingInWithID.update_forward_refs()
