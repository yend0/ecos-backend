import uuid

from typing import TYPE_CHECKING

from datetime import datetime, date

from sqlalchemy import String, Date, DateTime, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ecos_backend.db.models.base import Base


class User(Base):
    __tablename__: str = "User"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    first_name: Mapped[str | None] = mapped_column(String(32))
    middle_name: Mapped[str | None] = mapped_column(String(32))
    last_name: Mapped[str | None] = mapped_column(String(32))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    email_verified: Mapped[bool] = mapped_column(default=False)
    birth_date: Mapped[date | None] = mapped_column(Date)
    verification_code: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )

    if TYPE_CHECKING:
        from .accrual_history import AccrualHistory
        from .user_image import UserImage
        from .moderation import Moderation
        from .reception_point import ReceptionPoint

    user_image: Mapped[list["UserImage"]] = relationship(
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )

    accural_history: Mapped[list["AccrualHistory"]] = relationship(
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )

    moderation: Mapped[list["Moderation"]] = relationship(
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )

    reception_point: Mapped[list["ReceptionPoint"]] = relationship(
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )
