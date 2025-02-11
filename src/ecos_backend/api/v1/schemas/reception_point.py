import uuid
import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl


class ReceptionPointBaseSchema(BaseModel):
    name: str
    address: str
    user_id: uuid.UUID

    model_config: ConfigDict = ConfigDict(extra="forbid")


class ReceptionPointResponseSchema(ReceptionPointBaseSchema):
    id: uuid.UUID
    urls: list[HttpUrl]
    updated_at: datetime.datetime

    model_config: ConfigDict = ConfigDict(from_attributes=True)
