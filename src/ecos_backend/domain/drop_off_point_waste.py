import uuid

from dataclasses import dataclass

from ecos_backend.common.interfaces import model


@dataclass
class DropOffPointWasteModel(model.AbstractModel):
    waste_id: int
    reception_point_id: uuid.UUID

    def __post_init__(self) -> None:
        if not isinstance(self.reception_point_id, uuid.UUID):
            raise ValueError("Invalid reception_point_id.")
        if not isinstance(self.waste_id, uuid.UUID):
            raise ValueError("Invalid waste_id.")
