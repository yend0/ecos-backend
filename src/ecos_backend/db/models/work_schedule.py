import uuid

from typing import TYPE_CHECKING

from datetime import time

from sqlalchemy import Time, Enum, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ecos_backend.common import enums
from ecos_backend.db.models.base import Base


class WorkSchedule(Base):
    __tablename__: str = "Work_Schedule"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    day_of_week: Mapped[enums.DayOfWeek] = mapped_column(Enum(enums.DayOfWeek))
    open_time: Mapped[time | None] = mapped_column(default=Time)
    close_time: Mapped[time | None] = mapped_column(default=Time)

    reception_point_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("Reception_Point.id", ondelete="CASCADE")
    )

    if TYPE_CHECKING:
        from .reception_point import ReceptionPoint

    reception_point: Mapped["ReceptionPoint"] = relationship(
        back_populates="work_schedule"
    )
