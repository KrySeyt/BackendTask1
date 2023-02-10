from __future__ import annotations
from datetime import datetime

from enum import Enum
from pydantic import BaseModel, Field


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


Mailing.update_forward_refs()
MailingIn.update_forward_refs()
MailingOut.update_forward_refs()
MailingInWithID.update_forward_refs()
