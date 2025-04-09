import typing
import uuid
import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

from ecos_backend.api.v1.schemas.work_schedule import (
    WorkScheduleResponseSchema,
    WorkScheduleRequestCreateSchema,
)
from ecos_backend.api.v1.schemas.waste import WasteResponseSchema

from ecos_backend.common import config, enums


class ReceptionPointFilterParams(BaseModel):
    """Parameters for filtering reception points"""

    name: str | None = Field(
        None, min_length=2, max_length=100, description="Filter by name (partial match)"
    )
    address: str | None = Field(
        None, min_length=3, description="Filter by address (partial match)"
    )
    status: enums.PointStatus | None = Field(None, description="Filter by status")
    waste_type: uuid.UUID | None = Field(
        None, description="Filter by accepted waste type ID"
    )
    user_id: uuid.UUID | None = Field(None, description="Filter by owner user ID")
    created_after: datetime.datetime | None = Field(
        None, description="Filter points created after this date"
    )
    created_before: datetime.datetime | None = Field(
        None, description="Filter points created before this date"
    )

    model_config = ConfigDict(extra="forbid")


class PaginationParams(BaseModel):
    """Pagination parameters"""

    page: int = Field(1, ge=1, description="Page number (1-based)")
    per_page: int = Field(20, ge=1, le=100, description="Items per page (max 100)")


class ReceptionPointBaseSchema(BaseModel):
    name: str
    address: str
    description: str | None
    user_id: uuid.UUID
    status: enums.PointStatus

    model_config: ConfigDict = ConfigDict(extra="forbid")


class ReceptionPointRequestCreateSchema(BaseModel):
    name: str
    address: str
    description: str | None
    work_schedule: list[WorkScheduleRequestCreateSchema]


class ReceptionPointResponseSchema(ReceptionPointBaseSchema):
    id: uuid.UUID
    work_schedule: list[WorkScheduleResponseSchema] = Field(
        default_factory=list, description="Reception point work schedule"
    )
    waste: list[WasteResponseSchema] = Field(
        default_factory=list, description="Waste types"
    )
    image_urls: list[HttpUrl] = Field(
        default_factory=list,
        description="List of full image URLs for the reception point ",
    )
    updated_at: datetime.datetime

    model_config: ConfigDict = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    def set_image_urls(cls, data: typing.Any) -> typing.Any:
        """Generate full URLs for all reception point images."""
        if isinstance(data, dict):
            # Handle dictionary input
            point_id = str(data.get("id", ""))
            if "reception_image" in data:
                data["image_urls"] = [
                    f"{config.s3_config.ENDPOINT}/"
                    f"{config.s3_config.RECEPTION_POINT_BUCKET}/"
                    f"{point_id}/images/{img['filename']}"
                    for img in data["reception_image"]
                    if "filename" in img
                ]
                # Rename field for consistency
                data["images"] = data.pop("reception_image")

        elif hasattr(data, "id") and hasattr(data, "reception_image"):
            # Handle SQLAlchemy model input
            point_id = str(data.id)
            data.image_urls = [
                f"{config.s3_config.ENDPOINT}/"
                f"{config.s3_config.RECEPTION_POINT_BUCKET}/"
                f"{point_id}/images/{img.filename}"
                for img in data.reception_image
                if hasattr(img, "filename")
            ]
            # For backward compatibility
            if not hasattr(data, "images"):
                data.images = data.reception_image

        return data


class ReceptionPointListResponse(BaseModel):
    """Paginated response with reception points"""

    items: list[ReceptionPointResponseSchema] = Field(
        ..., description="List of reception points"
    )
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [],
                "total": 0,
                "page": 1,
                "per_page": 20,
                "total_pages": 0,
            }
        }
    )
