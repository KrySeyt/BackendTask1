from __future__ import annotations
from datetime import datetime
from pytz import all_timezones_set
from enum import Enum
from pydantic import BaseModel, Field, validator


class HashableBaseModel(BaseModel):
    def __hash__(self):
        return id(self)


class MailingBase(HashableBaseModel):
    text: str
    start_time: datetime
    end_time: datetime

    class Config:
        schema_extra = {
            "example": {
                "text": "string",
                "start_time": "2022-12-29T21:52:48.840Z",
                "end_time": "2022-12-29T21:52:48.840Z",
            }
        }


class Mailing(MailingBase):
    id: int
    clients_tags: list[MailingTag] = []
    clients_mobile_operator_codes: list[int] = []

    class Config(MailingBase.Config):
        schema_extra = {
            **MailingBase.Config.schema_extra,
            **{
                "example": {
                    **MailingBase.Config.schema_extra.get("example", {}),
                    **{
                        "id": 0,
                        "clients_tags": [
                            {
                                "text": "Any text"
                            }
                        ],
                        "clients_mobile_operator_codes": [
                            900, 910
                        ]
                    }
                }
            }
        }


class MailingIn(MailingBase):
    clients_tags: list[MailingTagIn] = []
    clients_mobile_operator_codes: list[int] = []

    class Config(MailingBase.Config):
        schema_extra = {
            **MailingBase.Config.schema_extra,
            **{
                "example": {
                    **MailingBase.Config.schema_extra.get("example", {}),
                    **{
                        "clients_tags": [
                            {
                                "text": "Any text"
                            }
                        ],
                        "clients_mobile_operator_codes": [
                            900, 910
                        ]
                    }
                }
            }
        }


class MailingInWithID(MailingIn):
    id: int

    class Config(MailingIn.Config):
        schema_extra = {
            **MailingIn.Config.schema_extra,
            **{
                "example": {
                    **MailingIn.Config.schema_extra.get("example", {}),
                    **{
                        "id": 0
                    }
                }
            }
        }


class MailingOut(MailingBase):
    id: int
    clients_tags: list[MailingTagOut] = []
    clients_mobile_operator_codes: list[int] = []

    class Config(MailingBase.Config):
        schema_extra = {
            **MailingBase.Config.schema_extra,
            **{
                "example": {
                    **MailingBase.Config.schema_extra.get("example", {}),
                    **{
                        "id": 0,
                        "clients_tags": [
                            {
                                "text": "Any text"
                            }
                        ],
                        "clients_mobile_operator_codes": [
                            900, 910
                        ]
                    }
                }
            }
        }


class MailingTagBase(BaseModel):
    text: str


class MailingTag(MailingTagBase):
    pass


class MailingTagOut(MailingTagBase):
    pass


class MailingTagIn(MailingTagBase):
    pass


class ClientBase(HashableBaseModel):
    phone_number: int = Field(ge=70000000000, le=79999999999)
    phone_operator_code: int
    timezone: str

    class Config:
        schema_extra = {
            "example": {
                "phone_number": 79009999999,
                "phone_operator_code": 900,
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
    tag: MailingTag


class ClientIn(ClientBase):
    tag: MailingTagIn

    class Config:
        schema_extra = {
            **ClientBase.Config.schema_extra,
            **{
                "example": {
                    **ClientBase.Config.schema_extra.get("example", {}),
                    **{
                        "tag":
                            {
                                "text": "Any text"
                            }
                    }
                }
            }
        }


class ClientInWithID(ClientIn):
    id: int
    tag: MailingTagIn


class ClientOut(ClientBase):
    id: int
    tag: MailingTagOut

    class Config:
        schema_extra = {
            **ClientBase.Config.schema_extra,
            **{
                "example": {
                    **ClientBase.Config.schema_extra.get("example", {}),
                    **{
                        "tag":
                            {
                                "text": "Any text"
                            }
                    }
                }
            }
        }


class MessageStatus(Enum):
    delivered = "delivered"
    not_delivered = "not delivered"


class Message(BaseModel):
    id: int
    created_at: datetime
    status: MessageStatus
    mailing_id: int
    client_id: int


class MailingStatsBase(BaseModel):
    messages: dict[MessageStatus, int]

    class Config:
        schema_extra = {
            "example": {
                "messages": {
                    status: 0 for status in MessageStatus
                }
            }
        }


class MailingStats(MailingStatsBase):
    mailing: Mailing

    class Config:
        schema_extra = {
            "example": {
                **MailingStatsBase.Config.schema_extra.get("example", {}),
                "mailing": Mailing.Config.schema_extra.get("example", {}),
            }
        }


class MailingStatsOut(MailingStatsBase):
    mailing: MailingOut

    class Config:
        schema_extra = {
            "example": {
                **MailingStatsBase.Config.schema_extra.get("example", {}),
                "mailing": MailingOut.Config.schema_extra.get("example", {}),
            }
        }


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
