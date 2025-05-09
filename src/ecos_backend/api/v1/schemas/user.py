import typing
import uuid
import re


from typing import Annotated
from datetime import date, datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    HttpUrl,
    EmailStr,
    Field,
    field_validator,
    model_validator,
    StringConstraints,
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
    email: EmailStr = Field(..., description="User email address")

    model_config: ConfigDict = ConfigDict(extra="forbid")


class UserRequestCreateSchema(UserBaseSchema):
    password: str = Field(
        ..., min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH
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
    id: uuid.UUID = Field(..., description="Unique user identifier")
    first_name: str | None = Field(
        None, max_length=MAX_NAME_LENGTH, description="User's first name"
    )
    middle_name: str | None = Field(
        None, max_length=MAX_NAME_LENGTH, description="User's middle name"
    )
    last_name: str | None = Field(
        None, max_length=MAX_NAME_LENGTH, description="User's last name"
    )
    birth_date: date | None = Field(None, description="User's birth date (YYYY-MM-DD)")
    image_url: HttpUrl | None = Field(None, description="URL to user's profile image")
    points: int = Field(default=0, ge=0, description="User's loyalty points")
    email_verified: bool = Field(default=False, description="Is email verified")
    created_at: datetime = Field(..., description="User registration timestamp")
    updated_at: datetime = Field(..., description="Last profile update timestamp")

    user_image: list[UserImageBaseSchema] = Field(
        default_factory=list, description="User's profile images"
    )
    accural_history: list[AccrualHistoryBaseSchema] = Field(
        default_factory=list, description="User's accrual history"
    )

    model_config: ConfigDict = ConfigDict(from_attributes=True)

    @property
    def full_name(self) -> str | None:
        if not any([self.first_name, self.middle_name, self.last_name]):
            return None
        return " ".join(
            filter(None, [self.first_name, self.middle_name, self.last_name])
        )

    @model_validator(mode="before")
    def set_image_url(cls, data: typing.Any) -> typing.Any:
        if isinstance(data, User) and hasattr(data, "user_image") and data.user_image:
            first_image: UserImage = data.user_image[0]
            data.image_url = f"{config.s3_config.ENDPOINT}/{config.s3_config.USER_BUCKET}/{data.id}/images/{first_image.filename}"
        return data

    @model_validator(mode="before")
    def set_points(cls, data: typing.Any) -> typing.Any:
        if (
            isinstance(data, User)
            and hasattr(data, "accural_history")
            and data.accural_history
        ):
            data.points = sum(item.points for item in data.accural_history)
        return data


class UserRequestUpdatePartialSchema(BaseModel):
    first_name: Annotated[str, StringConstraints(max_length=MAX_NAME_LENGTH)] | None = (
        Field(None, description="User's first name")
    )
    middle_name: (
        Annotated[str, StringConstraints(max_length=MAX_NAME_LENGTH)] | None
    ) = Field(None, description="User's middle name")
    last_name: Annotated[str, StringConstraints(max_length=MAX_NAME_LENGTH)] | None = (
        Field(None, description="User's last name")
    )
    birth_date: date | None = Field(None, description="User's birth date (YYYY-MM-DD)")

    model_config: ConfigDict = ConfigDict(extra="forbid")

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, v: date | None) -> date | None:
        if v is not None and v > date.today():
            raise ValueError("Birth date cannot be in the future")
        return v

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "UserRequestUpdatePartialSchema":
        if not any(
            [self.first_name, self.middle_name, self.last_name, self.birth_date]
        ):
            raise ValueError("At least one field must be provided for update")
        return self
