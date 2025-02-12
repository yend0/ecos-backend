import uuid
from pydantic import BaseModel, ConfigDict, HttpUrl


class WasteBaseSchema(BaseModel):
    name: str
    description: str

    model_config: ConfigDict = ConfigDict(extra="forbid")


class WasteRequestCreateSchema(WasteBaseSchema):
    pass


class WasteResponseSchema(WasteBaseSchema):
    id: uuid.UUID
    image_url: HttpUrl

    model_config: ConfigDict = ConfigDict(from_attributes=True)
