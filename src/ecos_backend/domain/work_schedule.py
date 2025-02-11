from dataclasses import dataclass
import uuid
from datetime import time
from ecos_backend.common.interfaces import model


@dataclass
class WorkScheduleModel(model.AbstractModel):
    id: uuid.UUID
    day_of_week: int
    open_time: time
    close_time: time
    reception_point_id: uuid.UUID

    def __post_init__(self) -> None:
        if not isinstance(self.reception_point_id, uuid.UUID):
            raise ValueError("Invalid reception_point_id")
