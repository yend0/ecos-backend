import typing
import uuid
import re

from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    HttpUrl,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)

from ecos_backend.api.v1.schemas.user_image import UserImageBaseSchema
from ecos_backend.api.v1.schemas.accrual_history import AccrualHistoryBaseSchema
from ecos_backend.common import config
from ecos_backend.db.models.user import User
from ecos_backend.db.models.user_image import UserImage


MAX_NAME_LENGTH = 32
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 64
PASSWORD_PATTERN: re.Pattern[str] = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).+$"
)


class UserBaseSchema(BaseModel):
    """
    Base schema for user-related operations.

    Attributes:
        email (EmailStr): User email address.
    """

    email: EmailStr = Field(..., description="User email address")

    model_config: ConfigDict = ConfigDict(extra="forbid")


class UserRequestCreateSchema(UserBaseSchema):
    """
    Schema for user creation requests.

    Attributes:
        email (EmailStr): User email address.
        password (str): User password.

    Methods:
        validate_password(cls, value): Validates the password format.
        normalize_email(cls, v: str) -> str: Normalizes the email address.
    """

    password: str = Field(
        ...,
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
        description="User password",
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if not PASSWORD_PATTERN.match(value):
            raise ValueError(
                "Password must contain uppercase, lowercase, digit and special character"
            )
        return value

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class UserResponseSchema(UserBaseSchema):
    """
    Schema for user response.

    Attributes:
        id (uuid.UUID): Unique user identifier.
        email (EmailStr): User email address.
        image_url (HttpUrl | None): URL to user's profile image.
        points (int): User's loyalty points.
        email_verified (bool): Is email verified.
        created_at (datetime): User registration timestamp.
        updated_at (datetime): Last profile update timestamp.
        user_image (list[UserImageBaseSchema]): User's profile images.
        accural_history (list[AccrualHistoryBaseSchema]): User's accrual history.

    Methods:
        set_image_url(cls, data: typing.Any) -> typing.Any: Sets the image URL based on the first image.
        set_points(cls, data: typing.Any) -> typing.Any: Sets the points based on the accrual history.
    """

    id: uuid.UUID = Field(..., description="Unique user identifier")
    image_url: HttpUrl | None = Field(None, description="URL to user's profile image")
    points: int = Field(default=0, ge=0, description="User's loyalty points")
    email_verified: bool = Field(default=False, description="Is email verified")
    created_at: datetime = Field(..., description="User registration timestamp")
    updated_at: datetime = Field(..., description="Last profile update timestamp")

    user_images: list[UserImageBaseSchema] = Field(
        default_factory=list, description="User's profile images"
    )
    accural_histories: list[AccrualHistoryBaseSchema] = Field(
        default_factory=list, description="User's accrual history"
    )

    model_config: ConfigDict = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    def set_image_url(cls, data: typing.Any) -> typing.Any:
        if isinstance(data, User) and hasattr(data, "user_images") and data.user_images:
            first_image: UserImage = data.user_images[0]
            data.image_url = f"{config.s3_config.ENDPOINT}/{config.s3_config.USER_BUCKET}/{data.id}/images/{first_image.filename}"
        return data

    @model_validator(mode="before")
    def set_points(cls, data: typing.Any) -> typing.Any:
        if (
            isinstance(data, User)
            and hasattr(data, "accural_histories")
            and data.accural_histories
        ):
            data.points = sum(item.points for item in data.accural_histories)
        return data


class UserRequestUpdatePartialSchema(BaseModel):
    """
    Schema for partial user update requests.
    """

    model_config: ConfigDict = ConfigDict(extra="forbid")
