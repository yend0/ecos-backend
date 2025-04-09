import uuid

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ecos_backend.db.models.base import Base


class ReceptionImage(Base):
    __tablename__: str = "Reception_Image"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    filename: Mapped[str] = mapped_column(String(255))

    reception_point_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("Reception_Point.id", ondelete="CASCADE")
    )

    if TYPE_CHECKING:
        from .reception_point import ReceptionPoint

    reception_point: Mapped["ReceptionPoint"] = relationship(
        back_populates="reception_image"
    )
