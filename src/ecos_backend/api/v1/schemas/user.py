import uuid
import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl


class UserBaseSchema(BaseModel):
    phone_number: str

    model_config: ConfigDict = ConfigDict(extra="forbid")


class UserCreateSchema(UserBaseSchema):
    password: str


class UserSchema(UserBaseSchema):
    id: uuid.UUID
    birth_date: datetime.date | None = None
    image_url: HttpUrl | None = None

    model_config: ConfigDict = ConfigDict(from_attributes=True)
