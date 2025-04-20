import uuid

from datetime import time

from pydantic import BaseModel, ConfigDict

from ecos_backend.common import enums


class WorkScheduleBaseSchema(BaseModel):
    day_of_week: enums.DayOfWeek
    open_time: time | None = None
    close_time: time | None = None

    model_config: ConfigDict = ConfigDict(extra="forbid")


class WorkScheduleRequestCreateSchema(WorkScheduleBaseSchema):
    pass


class WorkScheduleResponseSchema(WorkScheduleBaseSchema):
    id: uuid.UUID
    model_config: ConfigDict = ConfigDict(from_attributes=True)
