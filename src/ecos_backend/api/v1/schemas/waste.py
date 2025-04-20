import uuid
import re

from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    HttpUrl,
    ValidationInfo,
    field_validator,
    Field,
    StringConstraints,
)


class WasteBaseSchema(BaseModel):
    name: Annotated[
        str,
        StringConstraints(
            min_length=2,
            max_length=100,
        ),
    ] = Field(..., description="Full name of waste material (2-100 chars)")

    description: Annotated[str, StringConstraints(min_length=10, max_length=1000)] = (
        Field(..., description="Detailed description (10-1000 chars)")
    )

    abbreviated_name: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=10,
        ),
    ] = Field(..., description="Short code (1-10 uppercase chars)")

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "name": "Полиэтилен PET",
                    "description": "Полиэтилентерефталат, используется для бутылок",
                    "abbreviated_name": "PET",
                }
            ]
        },
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if re.search(r"\s{2,}", v):
            raise ValueError("Name contains multiple spaces")
        return v

    @field_validator("abbreviated_name")
    @classmethod
    def validate_abbr(cls, v: str) -> str:
        if v.isdigit():
            raise ValueError("Abbreviation cannot be numbers only")
        return v


class WasteRequestCreateSchema(WasteBaseSchema):
    @field_validator("name")
    @classmethod
    def validate_unique_name(cls, v: str, values: ValidationInfo) -> str:
        return v


class WasteResponseSchema(WasteBaseSchema):
    id: uuid.UUID = Field(..., description="Unique waste identifier")
    image_url: HttpUrl | None = Field(
        None, description="URL of waste image if available"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "name": "Полиэтилен PET",
                    "description": "Полиэтилентерефталат, используется для бутылок",
                    "abbreviated_name": "PET",
                    "image_url": "https://storage.example.com/waste/pet.jpg",
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z",
                }
            ]
        },
    )

    @field_validator("image_url", mode="before")
    @classmethod
    def validate_image_url(cls, v: str | None) -> str | None:
        if v and not v.startswith(("http://", "https://")):
            raise ValueError("Image URL must start with http:// or https://")
        return v
