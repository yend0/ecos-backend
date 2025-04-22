import uuid
import datetime
from pydantic import BaseModel, ConfigDict

from ecos_backend.common import enums


class AccrualHistoryBaseSchema(BaseModel):
    id: uuid.UUID
    points: int
    reward: enums.RewardType
    created_at: datetime.datetime

    model_config: ConfigDict = ConfigDict(extra="forbid", from_attributes=True)
