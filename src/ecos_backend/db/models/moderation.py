import uuid

from typing import TYPE_CHECKING

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ecos_backend.db.models.base import Base


class Moderation(Base):
    __tablename__: str = "Moderation"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    comment: Mapped[str | None]
    verification_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("User.id", ondelete="CASCADE")
    )

    reception_point_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("Reception_Point.id", ondelete="CASCADE")
    )

    if TYPE_CHECKING:
        from .user import User
        from .reception_point import ReceptionPoint

    user: Mapped["User"] = relationship(back_populates="moderation")
    reception_point: Mapped["ReceptionPoint"] = relationship(
        back_populates="moderation"
    )
