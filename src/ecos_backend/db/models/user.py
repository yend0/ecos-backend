import uuid

from typing import TYPE_CHECKING

from datetime import datetime

from sqlalchemy import String, DateTime, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ecos_backend.db.models.base import Base


class User(Base):
    __tablename__: str = "User"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    email: Mapped[str] = mapped_column(String(255), unique=True)
    email_verified: Mapped[bool] = mapped_column(default=False)
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
        from .user_achievement import UserAchievement
        from .reception_point import ReceptionPoint

    user_images: Mapped[list["UserImage"]] = relationship(
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )

    achievements: Mapped[list["UserAchievement"]] = relationship(
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )

    accural_histories: Mapped[list["AccrualHistory"]] = relationship(
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )

    reception_points: Mapped[list["ReceptionPoint"]] = relationship(
        back_populates="users", secondary="Reception_Point_Submission"
    )
