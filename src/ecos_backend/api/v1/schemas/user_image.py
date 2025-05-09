import uuid
from pydantic import BaseModel, ConfigDict, Field


class UserImageBaseSchema(BaseModel):
    """
    Base schema for user images.

    Attributes:
        id (uuid.UUID): Unique identifier for the image.
        filename (str | None): Name of the image file.
    """

    id: uuid.UUID = Field(..., description="Unique identifier for the image")
    filename: str | None = Field(None, description="Name of the image file")
    model_config: ConfigDict = ConfigDict(from_attributes=True)
