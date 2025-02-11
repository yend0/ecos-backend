from dataclasses import dataclass
import uuid
from ecos_backend.common.interfaces import model


@dataclass
class DropOffPointWasteModel(model.AbstractModel):
    waste_id: int
    reception_point_id: uuid.UUID

    def __post_init__(self) -> None:
        if not isinstance(self.reception_point_id, uuid.UUID):
            raise ValueError("Invalid reception_point_id.")
