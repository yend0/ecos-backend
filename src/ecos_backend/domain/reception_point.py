from dataclasses import dataclass
import uuid
from datetime import datetime
from ecos_backend.common.interfaces import model


@dataclass
class ReceptionPointModel(model.AbstractModel):
    id: uuid.UUID
    name: str
    address: str
    updated_at: datetime
    user_id: uuid.UUID
    images_url: str = None

    def __post_init__(self) -> None:
        if len(self.name) < 1 or len(self.address) < 1:
            raise ValueError("Reception Point name and address cannot be empty.")
