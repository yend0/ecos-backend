import uuid

from pydantic import BaseModel, ConfigDict, field_validator


class ReceptionImageBaseSchema(BaseModel):
    """
    Schema representing a reception point image with URL generation.

    Attributes:
        id: Unique identifier for the image
        filename: Original filename of the image
        url: Full accessible URL of the image
    """

    id: uuid.UUID
    filename: str

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "filename": "image.jpg",
                "url": "https://storage.example.com/reception-points/550e8400-e29b-41d4-a716-446655440000/images/image.jpg",
            }
        },
    )

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, v: str) -> str:
        """Validate filename doesn't contain path traversal characters."""
        if "/" in v or "\\" in v or ".." in v:
            raise ValueError("Filename contains invalid characters")
        return v
