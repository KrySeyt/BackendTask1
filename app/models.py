from __future__ import annotations
from datetime import datetime
from typing import Any, Sequence, Iterable

from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey, Table
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import relationship
from sqlalchemy_utils import PhoneNumberType, PhoneNumber

from .database import Base
from .schema import MessageStatus


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

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(), nullable=False)
    clients_tags: list[MailingTag] = relationship("MailingTag",
                                                  secondary=mailings_and_mailing_tags_association,
                                                  lazy="subquery")
    clients_mobile_operator_codes: list[MailingMobileOperatorCode] = \
        relationship("MailingMobileOperatorCode",
                     secondary=mailings_and_operator_codes_association,
                     lazy="subquery")
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

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
            clients_mobile_operator_codes=codes,
            text=text,
            start_time=start_time,
            end_time=end_time)


class MailingTag(Base):
    __tablename__ = "mailing_tags"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, unique=True)

    def __init__(self, text: str, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.text = text


class MailingMobileOperatorCode(Base):
    __tablename__ = "mailing_mobile_operator_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(Integer, nullable=False, unique=True)

    def __init__(self, code: int, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.code = code


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    phone_number: PhoneNumber = Column(PhoneNumberType())
    phone_operator_code = Column(Integer)
    tag_id = Column(Integer, ForeignKey("mailing_tags.id"))
    tag: MailingTag = relationship("MailingTag", lazy="subquery")
    timezone = Column(String, default="Europe/Amsterdam")

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
            tag_id=tag.id,
            tag=tag,
            timezone=timezone
        )


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.now)
    status = Column(Enum(MessageStatus), default=MessageStatus.not_delivered)
    mailing_id = Column(Integer, nullable=False)
    client_id = Column(Integer, nullable=False)

    @classmethod
    async def create(cls, *args: Any, **kwargs: Any) -> Message:
        return cls(*args, **kwargs)
