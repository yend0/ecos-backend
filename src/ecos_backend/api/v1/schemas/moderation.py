import datetime
import uuid

from pydantic import BaseModel, ConfigDict, Field

from ecos_backend.common import enums


class ModerationBaseSchema(BaseModel):
    """
    Base schema for moderation entries.

    Attributes:
        id (uuid.UUID): Unique identifier for the moderation entry.
        user_id (uuid.UUID): ID of the user who created the moderation entry.
        reception_point_id (uuid.UUID): ID of the reception point being moderated.
        verification_date (datetime.datetime): Date of verification.
        comment (str | None): Comment or note about the moderation entry.
    """

    id: uuid.UUID = Field(..., description="Unique identifier for the moderation entry")
    user_id: uuid.UUID = Field(
        ..., description="ID of the user who created the moderation entry"
    )
    reception_point_id: uuid.UUID = Field(
        ..., description="ID of the reception point being moderated"
    )
    verification_date: datetime.datetime = Field(
        ..., description="Date of verification"
    )
    comment: str | None = Field(
        None, description="Comment or note about the moderation entry"
    )

    model_config: ConfigDict = ConfigDict(extra="forbid")


class ModerationRequestCreateSchema(BaseModel):
    """
    Schema for creating a new moderation entry.

    Attributes:
        status (enums.PointStatus): Status of the moderation entry.
        comment (str | None): Comment or note about the moderation entry.
    """

    status: enums.PointStatus = Field(..., description="Status of the moderation entry")
    comment: str | None = Field(
        None, description="Comment or note about the moderation entry"
    )

    model_config: ConfigDict = ConfigDict(extra="forbid")


class ModerationResponseSchema(ModerationBaseSchema):
    """
    Schema for the response of a moderation entry.

    Attributes:
        id (uuid.UUID): Unique identifier for the moderation entry.
        user_id (uuid.UUID): ID of the user who created the moderation entry.
        reception_point_id (uuid.UUID): ID of the reception point being moderated.
        verification_date (datetime.datetime): Date of verification.
        comment (str | None): Comment or note about the moderation entry.
    """

    model_config: ConfigDict = ConfigDict(from_attributes=True)
