from __future__ import annotations

from pytz import all_timezones_set
from pydantic import validator, Field
from sqlalchemy_utils import PhoneNumber

from src.mailings.schema import MailingTag, MailingTagIn, MailingTagOut
from src.schema import HashableBase


class ClientBase(HashableBase):
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
