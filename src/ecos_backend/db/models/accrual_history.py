import uuid

from typing import TYPE_CHECKING

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ecos_backend.common import enums
from ecos_backend.db.models.base import Base


class AccrualHistory(Base):
    __tablename__: str = "Accrual_History"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    reward: Mapped[enums.RewardType] = mapped_column(Enum(enums.RewardType))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )
    points: Mapped[int] = mapped_column(default=0)

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("User.id", ondelete="CASCADE")
    )

    if TYPE_CHECKING:
        from .user import User
    user: Mapped["User"] = relationship(back_populates="accural_history")
