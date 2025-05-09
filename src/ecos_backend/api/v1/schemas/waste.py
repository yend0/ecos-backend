import uuid

from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    HttpUrl,
    field_validator,
    Field,
    StringConstraints,
)

from ecos_backend.api.v1.schemas.waste_translation import (
    WasteTranslationRequestCreateSchema,
    WasteTranslationResponseSchema,
)


class WasteBaseSchema(BaseModel):
    """
    Base schema for waste material
    Attributes:
        abbreviated_name (str): Short code (1-10 uppercase chars)
    Methods:
        validate_abbr: Validates the abbreviated_name field to ensure it does not contain numbers only
    """

    abbreviated_name: Annotated[
        str,
        StringConstraints(min_length=1, max_length=10),
    ] = Field(..., description="Short code (1-10 uppercase chars)")

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "abbreviated_name": "PET",
                }
            ]
        },
    )

    @field_validator("abbreviated_name")
    @classmethod
    def validate_abbr(cls, v: str) -> str:
        if v.isdigit():
            raise ValueError("Abbreviation cannot be numbers only")
        return v


class WasteRequestCreateSchema(WasteBaseSchema):
    """
    Schema for creating a new waste material
    Attributes:
        abbreviated_name (str): Short code (1-10 uppercase chars)
        waste_translations (list[WasteTranslationRequestCreateSchema]): List of translations for the waste material
    """

    waste_translations: list[WasteTranslationRequestCreateSchema] = Field(
        ..., description="List of translations for the waste material"
    )


class WasteResponseBaseSchema(WasteBaseSchema):
    """
    Base schema for waste material response
    Attributes:
        id (uuid.UUID): Unique waste identifier
        image_url (HttpUrl | None): URL of waste image if available
    Methods:
        validate_image_url: Validates the image_url field to ensure it starts with http:// or https://
    """

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
                    "abbreviated_name": "PET",
                    "image_url": "https://storage.example.com/waste/pet.jpg",
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


class WasteResponseSchema(WasteResponseBaseSchema):
    """
    Schema for waste material response
    Attributes:
        id (uuid.UUID): Unique waste identifier
        abbreviated_name (str): Short code (1-10 uppercase chars)
        image_url (HttpUrl | None): URL of waste image if available
        waste_translations (list[WasteTranslationResponseSchema]): List of translations for the waste material
    """

    waste_translations: list[WasteTranslationResponseSchema] = Field(
        ..., description="List of translations for the waste material"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "abbreviated_name": "PET",
                    "image_url": "https://storage.example.com/waste/pet.jpg",
                    "waste_translations": [
                        {
                            "id": "550e8400-e29b-41d4-a716-446655440001",
                            "name": "Полиэтилен PET",
                            "description": "Полиэтилентерефталат, используется для бутылок",
                            "language_code": "ru",
                        }
                    ],
                }
            ]
        },
    )
