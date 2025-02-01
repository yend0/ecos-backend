from pydantic import BaseModel, ConfigDict


class BaseInforamtionResponse(BaseModel):
    status: str
    message: str

    model_config: ConfigDict = ConfigDict(extra="forbid")
