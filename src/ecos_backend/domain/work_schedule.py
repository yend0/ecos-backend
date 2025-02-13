import uuid

from dataclasses import dataclass, field
from datetime import time

from ecos_backend.common.interfaces import model
from ecos_backend.common import enums


@dataclass
class WorkScheduleModel(model.AbstractModel):
    day_of_week: enums.Day
    open_time: time | None = None
    close_time: time | None = None
    reception_point_id: uuid.UUID | None = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def __post_init__(self) -> None:
        pass

    def set_reception_point_id(self, reception_point_id: uuid.UUID) -> None:
        self.reception_point_id = reception_point_id
