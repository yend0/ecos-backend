import uuid
import re

from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    field_validator,
    Field,
    StringConstraints,
)


class WasteTranslationBaseSchema(BaseModel):
    """
    Base schema for waste translation

    Attributes:
        waste_id (uuid.UUID): Unique waste identifier
    """

    waste_id: uuid.UUID | None = Field(None, description="Unique waste identifier")


class WasteTranslationRequestCreateSchema(WasteTranslationBaseSchema):
    """
    Schema for creating a new waste translation

    Attributes:
        name (str): Full name of waste material (2-100 chars)
        description (str): Detailed description (10-1000 chars)
        language_code (str): Language code (ISO 639-1)
        waste_id (uuid.UUID): Unique waste identifier
    Methods:
        validate_name: Validates the name field to ensure it does not contain multiple spaces
    """

    name: Annotated[str, StringConstraints(min_length=2, max_length=100)] = Field(
        ..., description="Full name of waste material (2-100 chars)"
    )
    description: Annotated[str, StringConstraints(min_length=10, max_length=1000)] = (
        Field(..., description="Detailed description (10-1000 chars)")
    )
    language_code: Annotated[str, StringConstraints(min_length=2, max_length=10)] = (
        Field(..., description="Language code (ISO 639-1)")
    )

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "name": "Полиэтилен PET",
                    "description": "Полиэтилентерефталат, используется для бутылок",
                    "language_code": "ru",
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


class WasteTranslationRequestUpdatePartialSchema(BaseModel):
    """
    Schema for updating a waste translation

    Attributes:
        name (str): Full name of waste material (2-100 chars)
        description (str): Detailed description (10-1000 chars)
    Methods:
        validate_name: Validates the name field to ensure it does not contain multiple spaces
    """

    name: Annotated[str, StringConstraints(min_length=2, max_length=100)] | None = (
        Field(None, description="Full name of waste material (2-100 chars)")
    )
    description: (
        Annotated[str, StringConstraints(min_length=10, max_length=1000)] | None
    ) = Field(None, description="Detailed description (10-1000 chars)")

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "name": "Полиэтилен PET",
                    "description": "Полиэтилентерефталат, используется для бутылок",
                    "language_code": "ru",
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


class WasteTranslationResponseSchema(WasteTranslationBaseSchema):
    """
    Schema for waste translation response


    Attributes:
        id (uuid.UUID): Unique waste identifier
        name (str): Full name of waste material (2-100 chars)
        description (str): Detailed description (10-1000 chars)
        language_code (str): Language code (ISO 639-1)
    """

    id: uuid.UUID = Field(..., description="Unique waste identifier")
    name: Annotated[str, StringConstraints(min_length=2, max_length=100)] = Field(
        ..., description="Full name of waste material (2-100 chars)"
    )
    description: Annotated[str, StringConstraints(min_length=10, max_length=1000)] = (
        Field(..., description="Detailed description (10-1000 chars)")
    )
    language_code: Annotated[str, StringConstraints(min_length=2, max_length=10)] = (
        Field(..., description="Language code (ISO 639-1)")
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "name": "Полиэтилен PET",
                    "description": "Полиэтилентерефталат, используется для бутылок",
                    "language_code": "ru",
                    "waste_id": "550e8400-e29b-41d4-a716-446655440000",
                }
            ]
        },
    )
