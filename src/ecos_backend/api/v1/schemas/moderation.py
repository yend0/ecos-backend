import datetime
import uuid

from pydantic import BaseModel, ConfigDict

from ecos_backend.common import enums


class ModerationBaseSchema(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    reception_point_id: uuid.UUID
    verification_date: datetime.datetime
    comment: str | None

    model_config: ConfigDict = ConfigDict(extra="forbid")


class ModerationRequestCreateSchema(BaseModel):
    status: enums.PointStatus
    comment: str | None

    model_config: ConfigDict = ConfigDict(extra="forbid")


class ModerationResponseSchema(ModerationBaseSchema):
    model_config: ConfigDict = ConfigDict(from_attributes=True)
