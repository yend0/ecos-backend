import uuid
import datetime
from pydantic import BaseModel, ConfigDict, Field

from ecos_backend.common import enums


class AccrualHistoryBaseSchema(BaseModel):
    """
    Schema representing the history of points accrued by a user.
    This schema includes the unique identifier, the number of points accrued,
    the type of reward associated with the points, and the date and time when
    the points were accrued.
    Attributes:
        id (uuid.UUID): Unique identifier for the accrual history entry.
        points (int): Number of points accrued.
        reward (enums.RewardType): Type of reward for the accrued points.
        created_at (datetime.datetime): Date and time when the points were accrued.
    """

    id: uuid.UUID = Field(
        ..., description="Unique identifier for the accrual history entry"
    )
    points: int = Field(..., description="Number of points accrued")
    reward: enums.RewardType = Field(
        ..., description="Type of reward for the accrued points"
    )
    created_at: datetime.datetime = Field(
        ..., description="Date and time when the points were accrued"
    )

    model_config: ConfigDict = ConfigDict(extra="forbid", from_attributes=True)
