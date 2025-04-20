import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from ecos_backend.db.models.base import Base


class ReceptionPointWaste(Base):
    __tablename__: str = "Reception_Point_Waste"

    waste_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("Waste.id", ondelete="CASCADE"), primary_key=True
    )
    reception_point_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("Reception_Point.id", ondelete="CASCADE"), primary_key=True
    )
