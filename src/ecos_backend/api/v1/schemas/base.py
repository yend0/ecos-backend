from pydantic import BaseModel, ConfigDict

from ecos_backend.common import enums


class BaseInforamtionResponse(BaseModel):
    status: enums.Status
    message: str

    model_config: ConfigDict = ConfigDict(extra="forbid")
