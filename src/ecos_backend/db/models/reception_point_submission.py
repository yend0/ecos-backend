import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from ecos_backend.db.models.base import Base


class ReceptionPointSubmission(Base):
    __tablename__: str = "Reception_Point_Submission"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("User.id", ondelete="CASCADE"), primary_key=True
    )
    reception_point_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("Reception_Point.id", ondelete="CASCADE"), primary_key=True
    )
