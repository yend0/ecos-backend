import uuid

from dataclasses import dataclass, field
from datetime import time

from ecos_backend.common.interfaces import model
from ecos_backend.common import enums


@dataclass
class WorkScheduleModel(model.AbstractModel):
    day_of_week: enums.Day
    open_time: time
    close_time: time
    reception_point_id: uuid.UUID = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def __post_init__(self) -> None:
        if not isinstance(self.reception_point_id, uuid.UUID):
            raise ValueError("Invalid reception_point_id")
        if not isinstance(self.id, uuid.UUID):
            raise ValueError("Invalid id")
