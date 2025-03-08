import uuid

from pydantic import BaseModel, ConfigDict

from ecos_backend.common import enums


class AccrualHistoryBaseSchema(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    points: int
    reward: enums.RewardType

    model_config: ConfigDict = ConfigDict(extra="forbid")


class AccrualHistoryResponseSchema(AccrualHistoryBaseSchema):
    model_config: ConfigDict = ConfigDict(from_attributes=True)
