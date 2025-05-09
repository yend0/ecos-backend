import uuid

from typing import TYPE_CHECKING

from sqlalchemy import String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ecos_backend.db.models.base import Base


class Waste(Base):
    __tablename__: str = "Waste"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    abbreviated_name: Mapped[str] = mapped_column(String(32), unique=True)
    image_url: Mapped[str | None] = mapped_column(String(255), unique=True)

    if TYPE_CHECKING:
        from .reception_point import ReceptionPoint
        from .waste_translation import WasteTranslation

    reception_points: Mapped[list["ReceptionPoint"]] = relationship(
        back_populates="wastes", secondary="Reception_Point_Waste"
    )

    waste_translations: Mapped[list["WasteTranslation"]] = relationship(
        back_populates="waste",
        cascade="all, delete-orphan",
    )
