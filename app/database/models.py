from __future__ import annotations
from datetime import datetime
from typing import Any, Sequence, Iterable

from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import relationship, Mapped, DeclarativeBase, mapped_column
from sqlalchemy_utils import PhoneNumberType, PhoneNumber

from app.mailing_service.schema import MessageStatus


class Base(DeclarativeBase):
    pass


mailings_and_mailing_tags_association = Table(
    "mailings_and_mailing_tags_table",
    Base.metadata,
    Column("mailing_id", ForeignKey("mailings.id")),
    Column("mailing_tag_id", ForeignKey("mailing_tags.id")),
)

mailings_and_operator_codes_association = Table(
    "mailings_and_operator_codes_table",
    Base.metadata,
    Column("mailing_id", ForeignKey("mailings.id")),
    Column("mailing_mobile_operator_codes_id", ForeignKey("mailing_mobile_operator_codes.id")),
)


class Mailing(Base):
    __tablename__ = "mailings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    text: Mapped[str]
    clients_tags: Mapped[list[MailingTag]] = relationship(secondary=mailings_and_mailing_tags_association,
                                                          lazy="subquery")
    _clients_mobile_operator_codes: Mapped[list[MailingMobileOperatorCode]] = \
        relationship(
                     secondary=mailings_and_operator_codes_association,
                     lazy="subquery")
    start_time: Mapped[datetime]
    end_time: Mapped[datetime]

    @property
    def clients_mobile_operator_codes(self) -> list[int]:
        return [value for i in self._clients_mobile_operator_codes if (value := i.code)]

    @clients_mobile_operator_codes.setter
    def clients_mobile_operator_codes(self, value: list[MailingMobileOperatorCode]) -> None:
        self._clients_mobile_operator_codes = value

    @classmethod
    async def create(cls,
                     db: AsyncSession,
                     clients_tags: Sequence[str],
                     clients_mobile_operator_codes: Sequence[int],
                     text: str,
                     start_time: datetime,
                     end_time: datetime) -> Mailing:
        existed_tags = (await db.execute(
            select(MailingTag).filter(MailingTag.text.in_(clients_tags)
                                      ))).scalars().all()
        existed_tags_texts: Iterable[Any] = map(lambda x: x.text, existed_tags)
        new_tags = map(MailingTag, filter(lambda x: x not in existed_tags_texts, clients_tags))
        tags = [*existed_tags, *new_tags]

        existed_codes = (await db.execute(
            select(MailingMobileOperatorCode).filter(MailingMobileOperatorCode.code.in_(clients_mobile_operator_codes)
                                                     ))).scalars().all()
        existed_codes_ints: Iterable[Any] = map(lambda x: x.code, existed_codes)
        new_codes = map(MailingMobileOperatorCode, filter(lambda x: x not in existed_codes_ints,
                                                          clients_mobile_operator_codes))
        codes = [*existed_codes, *new_codes]
        return cls(
            clients_tags=tags,
            _clients_mobile_operator_codes=codes,
            text=text,
            start_time=start_time,
            end_time=end_time)


class MailingTag(Base):
    __tablename__ = "mailing_tags"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    text: Mapped[str] = mapped_column(unique=True)

    def __init__(self, text: str, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.text = text


class MailingMobileOperatorCode(Base):
    __tablename__ = "mailing_mobile_operator_codes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[int] = mapped_column(unique=True)

    def __init__(self, code: int, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.code = code


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    phone_number: Mapped[PhoneNumber] = mapped_column(type_=PhoneNumberType())
    phone_operator_code: Mapped[int]
    tag_id: Mapped[int] = mapped_column(ForeignKey("mailing_tags.id"))
    tag: Mapped[MailingTag] = relationship(lazy="subquery")
    timezone: Mapped[str] = mapped_column(default="Europe/Amsterdam")

    @classmethod
    async def create(cls,
                     db: AsyncSession,
                     phone_number: str,
                     phone_operator_code: int,
                     tag_text: str,
                     timezone: str) -> Client:
        tag = (await db.execute(select(MailingTag).filter(MailingTag.text == tag_text))).scalar()
        if not tag:
            tag = MailingTag(text=tag_text)
            db.add(tag)
            await db.commit()
            await db.refresh(tag)
        return cls(
            phone_number=phone_number,
            phone_operator_code=phone_operator_code,
            tag=tag,
            timezone=timezone
        )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    status: Mapped[MessageStatus] = mapped_column(default=MessageStatus.not_delivered)
    mailing_id: Mapped[int]
    client_id: Mapped[int]

    @classmethod
    async def create(cls, *args: Any, **kwargs: Any) -> Message:
        return cls(*args, **kwargs)
