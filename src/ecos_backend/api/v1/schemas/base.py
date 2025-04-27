from pydantic import BaseModel, ConfigDict, Field

from ecos_backend.common import enums


class BaseInforamtionResponse(BaseModel):
    """
    Base schema for information responses.
    Attributes:
        status (enums.Status): Status of the request
        message (str): Message of the request
    """

    status: enums.Status = Field(..., description="Status of the request")
    message: str = Field(..., description="Message of the request")

    model_config: ConfigDict = ConfigDict(extra="forbid")
