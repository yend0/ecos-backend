import uuid
import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl


class UserBaseSchema(BaseModel):
    email: str

    model_config: ConfigDict = ConfigDict(extra="forbid")


class UserRequestCreateSchema(UserBaseSchema):
    password: str


class UserResponseSchema(UserBaseSchema):
    id: uuid.UUID
    birth_date: datetime.date | None = None
    image_url: HttpUrl | None = None
    first_name: str | None = None
    last_name: str | None = None

    model_config: ConfigDict = ConfigDict(from_attributes=True)
