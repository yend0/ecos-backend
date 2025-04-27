import typing
import uuid
import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

from ecos_backend.api.v1.schemas.work_schedule import (
    WorkScheduleResponseSchema,
    WorkScheduleRequestCreateSchema,
)
from ecos_backend.api.v1.schemas.waste import WasteResponseBaseSchema

from ecos_backend.common import config, enums


class Location(BaseModel):
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")


class ReceptionPointFilterParams(BaseModel):
    """Parameters for filtering reception points

    Attributes:
        name (str | None): Filter by name (partial match).
        address (str | None): Filter by address (partial match).
        radius (float | None): Filter by radius (between 0 and 100 km).
        status (enums.PointStatus | None): Filter by status.
        waste_type (uuid.UUID | None): Filter by accepted waste type ID.
    """

    name: str | None = Field(
        None, min_length=2, max_length=100, description="Filter by name (partial match)"
    )
    address: str | None = Field(
        None, min_length=3, description="Filter by address (partial match)"
    )
    radius: float | None = Field(
        None,
        ge=0.0,
        le=10000.0,
        description="Filter by radius (between 0 and 10000 m)",
    )
    status: enums.PointStatus | None = Field(None, description="Filter by status")
    waste_type: uuid.UUID | None = Field(
        None, description="Filter by accepted waste type ID"
    )

    model_config = ConfigDict(extra="forbid")


class PaginationParams(BaseModel):
    """
    Pagination parameters

    Attributes:
        page (int): Page number (1-based).
        per_page (int): Number of items per page (max 100).
    """

    page: int = Field(1, ge=1, description="Page number (1-based)")
    per_page: int = Field(20, ge=1, le=100, description="Items per page (max 100)")


class ReceptionPointBaseSchema(BaseModel):
    """
    Base schema for reception points

    Attributes:
        name (str): Reception point name.
        address (str): Reception point address.
        description (str | None): Reception point description.
        user_id (uuid.UUID): Owner user ID.
        status (enums.PointStatus): Reception point status.
        location (Location): Reception point location.
    """

    name: str = Field(
        ..., min_length=2, max_length=255, description="Reception point name"
    )
    address: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Reception point address",
    )
    description: str | None = Field(
        None, max_length=10000, description="Reception point description"
    )
    location: Location = Field(..., description="Reception point location")
    user_id: uuid.UUID = Field(..., description="Owner user ID")
    status: enums.PointStatus = Field(
        enums.PointStatus.UNDER_MODERATION,
        description="Reception point status",
    )

    model_config: ConfigDict = ConfigDict(extra="forbid")


class ReceptionPointRequestCreateSchema(BaseModel):
    """
    Schema for creating a new reception point

    Attributes:
        name (str): Reception point name.
        address (str): Reception point address.
        description (str | None): Reception point description.
        location (Location): Reception point location.
        work_schedules (list[WorkScheduleRequestCreateSchema]): Reception point work schedule.
    """

    name: str = Field(
        ..., min_length=2, max_length=255, description="Reception point name"
    )
    address: str = Field(
        ..., min_length=3, max_length=255, description="Reception point address"
    )
    description: str | None = Field(
        None, max_length=10000, description="Reception point description"
    )
    location: Location = Field(..., description="Reception point location")
    work_schedules: list[WorkScheduleRequestCreateSchema] = Field(
        default_factory=list, description="Reception point work schedule"
    )


class ReceptionPointResponseSchema(ReceptionPointBaseSchema):
    """
    Schema for reception point response
    Attributes:
        id (uuid.UUID): Reception point ID.
        name (str): Reception point name.
        address (str): Reception point address.
        description (str | None): Reception point description.
        location (Location): Reception point location.
        user_id (uuid.UUID): Owner user ID.
        status (enums.PointStatus): Reception point status.
        work_schedule (list[WorkScheduleResponseSchema]): Reception point work schedule.
        waste (list[WasteResponseBaseSchema]): Waste types.
        image_urls (list[HttpUrl]): List of full image URLs for the reception point.
        updated_at (datetime.datetime): Last update date.

    Methods:
        set_image_urls(cls, data: typing.Any) -> typing.Any: Generate full URLs for all reception point images.
    """

    id: uuid.UUID = Field(..., description="Reception point ID")
    work_schedules: list[WorkScheduleResponseSchema] = Field(
        default_factory=list, description="Reception point work schedule"
    )
    wastes: list[WasteResponseBaseSchema] = Field(
        default_factory=list, description="Waste types"
    )
    image_urls: list[HttpUrl] = Field(
        default_factory=list,
        description="List of full image URLs for the reception point ",
    )
    updated_at: datetime.datetime = Field(..., description="Last update date")

    model_config: ConfigDict = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    def set_image_urls(cls, data: typing.Any) -> typing.Any:
        """Generate full URLs for all reception point images."""
        if isinstance(data, dict):
            # Handle dictionary input
            point_id = str(data.get("id", ""))
            if "reception_images" in data:
                data["image_urls"] = [
                    f"{config.s3_config.ENDPOINT}/"
                    f"{config.s3_config.RECEPTION_POINT_BUCKET}/"
                    f"{point_id}/images/{img['filename']}"
                    for img in data["reception_image"]
                    if "filename" in img
                ]
                # Rename field for consistency
                data["images"] = data.pop("reception_image")

        elif hasattr(data, "id") and hasattr(data, "reception_images"):
            # Handle SQLAlchemy model input
            point_id = str(data.id)
            data.image_urls = [
                f"{config.s3_config.ENDPOINT}/"
                f"{config.s3_config.RECEPTION_POINT_BUCKET}/"
                f"{point_id}/images/{img.filename}"
                for img in data.reception_images
                if hasattr(img, "filename")
            ]
            # For backward compatibility
            if not hasattr(data, "images"):
                data.images = data.reception_images

        return data

    @model_validator(mode="before")
    def convert_location(cls, data: typing.Any) -> typing.Any:
        from geoalchemy2.elements import WKBElement
        from shapely.geometry import Point as ShapelyPoint
        from shapely import wkb

        """Convert location from database object to Location schema."""
        if isinstance(data, dict):
            loc = data.get("location")
            if isinstance(loc, WKBElement):
                shapely_point: ShapelyPoint = wkb.loads(bytes(loc.data))
                data["location"] = Location(
                    latitude=shapely_point.y,
                    longitude=shapely_point.x,
                )
        elif hasattr(data, "location"):
            loc = getattr(data, "location", None)
            if isinstance(loc, WKBElement):
                shapely_point: ShapelyPoint = wkb.loads(bytes(loc.data))
                data.location = Location(
                    latitude=shapely_point.y,
                    longitude=shapely_point.x,
                )
        return data


class ReceptionPointListResponse(BaseModel):
    """
    Paginated response with reception points

    Attributes:
        items (list[ReceptionPointResponseSchema]): List of reception points.
        total (int): Total number of items.
        page (int): Current page number.
        per_page (int): Number of items per page.
        total_pages (int): Total number of pages.
    """

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
