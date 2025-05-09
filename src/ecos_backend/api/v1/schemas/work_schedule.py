import uuid

from datetime import time

from pydantic import BaseModel, ConfigDict, Field

from ecos_backend.common.enums import DayOfWeek


class WorkScheduleBaseSchema(BaseModel):
    """
    Base schema for work schedule
    Attributes:
        day_of_week (DayOfWeek): Day of the week
        open_time (time | None): Opening time
        close_time (time | None): Closing time
    """

    day_of_week: DayOfWeek = Field(..., description="Day of the week")
    open_time: time | None = Field(None, description="Opening time")
    close_time: time | None = Field(None, description="Closing time")

    model_config: ConfigDict = ConfigDict(extra="forbid")


class WorkScheduleRequestCreateSchema(WorkScheduleBaseSchema):
    """
    Schema for creating a new work schedule
    Attributes:
        day_of_week (DayOfWeek): Day of the week
        open_time (time | None): Opening time
        close_time (time | None): Closing time
    """

    pass


class WorkScheduleResponseSchema(WorkScheduleBaseSchema):
    """
    Schema for work schedule response
    Attributes:
        day_of_week (DayOfWeek): Day of the week
        open_time (time | None): Opening time
        close_time (time | None): Closing time
        id (uuid.UUID): Unique work schedule identifier
    """

    id: uuid.UUID = Field(..., description="Unique work schedule identifier")

    model_config: ConfigDict = ConfigDict(from_attributes=True)
