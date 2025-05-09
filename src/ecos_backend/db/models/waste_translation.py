import uuid

from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ecos_backend.common.enums import LanguageCode
from ecos_backend.db.models.base import Base


class WasteTranslation(Base):
    __tablename__: str = "Waste_Translation"
    __table_args__ = (
        UniqueConstraint("waste_id", "languagecode", name="uq_waste_lang"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    waste_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("Waste.id", ondelete="CASCADE")
    )
    language_code: Mapped[LanguageCode] = mapped_column(
        Enum(LanguageCode), name="languagecode"
    )
    name: Mapped[str] = mapped_column(String(64))
    description: Mapped[str]

    if TYPE_CHECKING:
        from .waste import Waste

    waste: Mapped["Waste"] = relationship(
        back_populates="waste_translations",
    )
