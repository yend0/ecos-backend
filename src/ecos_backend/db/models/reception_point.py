import uuid

from typing import TYPE_CHECKING

from datetime import datetime

from sqlalchemy import Enum, Float, ForeignKey, String, DateTime, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ecos_backend.common import enums
from ecos_backend.db.models.base import Base


class ReceptionPoint(Base):
    __tablename__: str = "Reception_Point"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None]
    address: Mapped[str] = mapped_column(String(255), unique=True)

    latitude: Mapped[float] = mapped_column(Float, nullable=False, server_default="0.0")
    longitude: Mapped[float] = mapped_column(
        Float, nullable=False, server_default="0.0"
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )
    status: Mapped[enums.PointStatus] = mapped_column(
        Enum(enums.PointStatus), default=enums.PointStatus.UNDER_MODERATION
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("User.id", ondelete="CASCADE")
    )

    if TYPE_CHECKING:
        from .user import User
        from .moderation import Moderation
        from .reception_image import ReceptionImage
        from .work_schedule import WorkSchedule
        from .waste import Waste

    user: Mapped["User"] = relationship(back_populates="reception_points")

    moderations: Mapped[list["Moderation"]] = relationship(
        back_populates="reception_point",
        cascade="all, delete",
        passive_deletes=True,
    )

    reception_images: Mapped[list["ReceptionImage"]] = relationship(
        back_populates="reception_point",
        cascade="all, delete",
        passive_deletes=True,
    )

    work_schedules: Mapped[list["WorkSchedule"]] = relationship(
        back_populates="reception_point",
        cascade="all, delete",
        passive_deletes=True,
    )

    wastes: Mapped[list["Waste"]] = relationship(
        back_populates="reception_points", secondary="Reception_Point_Waste"
    )
