from __future__ import annotations

from sqlalchemy import ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy_utils import PhoneNumberType, PhoneNumber

from src.mailings.models import MailingTag
from src.database import Base


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