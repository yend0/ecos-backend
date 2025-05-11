import uuid
from datetime import datetime

from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ecos_backend.common import enums
from ecos_backend.db.models.base import Base


class UserAchievement(Base):
    __tablename__: str = "User_Achievement"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("User.id", ondelete="CASCADE")
    )

    awarded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
    )
    achievement_type: Mapped[enums.AchievementType] = mapped_column(
        Enum(enums.AchievementType),
        name="achievement_type",
        nullable=False,
    )

    if TYPE_CHECKING:
        from .user import User
    user: Mapped["User"] = relationship(back_populates="achievements")
