import uuid

from dataclasses import dataclass, field
from datetime import datetime

from ecos_backend.common.interfaces import model


@dataclass
class ModerationDTO(model.AbstractModel):
    comment: str
    verification_date: datetime | None = None
    reception_point_id: uuid.UUID | None = None
    user_id: uuid.UUID | None = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def set_reception_point_id(self, reception_point_id: uuid.UUID) -> None:
        self.reception_point_id = reception_point_id

    def set_user_id(self, user_id: uuid.UUID) -> None:
        self.user_id = user_id
