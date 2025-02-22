import uuid
from dataclasses import dataclass

from ecos_backend.common.interfaces import model


@dataclass
class DropOffPointWasteDTO(model.AbstractModel):
    waste_id: uuid.UUID
    reception_point_id: uuid.UUID
