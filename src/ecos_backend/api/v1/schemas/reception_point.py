import uuid
import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl

from ecos_backend.api.v1.schemas import work_schedule as ws
from ecos_backend.common import enums


class ReceptionPointBaseSchema(BaseModel):
    name: str
    address: str
    description: str | None
    user_id: uuid.UUID
    status: enums.PointStatus

    model_config: ConfigDict = ConfigDict(extra="forbid")


class ReceptionPointRequestCreateSchema(BaseModel):
    name: str
    address: str
    description: str | None
    work_schedules: list[ws.WorkScheduleRequestCreateSchema]


class ReceptionPointResponseSchema(ReceptionPointBaseSchema):
    id: uuid.UUID
    urls: list[HttpUrl]
    work_schedules: list[ws.WorkScheduleResponseSchema]
    waste_ids: list[uuid.UUID]
    updated_at: datetime.datetime

    model_config: ConfigDict = ConfigDict(from_attributes=True)
