import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from ecos_backend.common import enums


class UserAchievementBaseSchema(BaseModel):
    """
    Base schema for user achievement.

    Attributes:
        id (uuid.UUID): Unique identifier for the image.
        filename (str | None): Name of the image file.
    """

    id: uuid.UUID = Field(..., description="Unique identifier for the image")
    awarded_at: datetime = Field(
        ..., description="Date and time when the achievement was awarded"
    )
    achievement_type: enums.AchievementType = Field(
        ..., description="Type of the achievement"
    )
    model_config: ConfigDict = ConfigDict(from_attributes=True)
