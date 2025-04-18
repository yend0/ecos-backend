import uuid
from pydantic import BaseModel, ConfigDict


class UserImageBaseSchema(BaseModel):
    id: uuid.UUID
    filename: str | None = None
    model_config: ConfigDict = ConfigDict(from_attributes=True)
