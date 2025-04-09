import typing

from fastapi import Depends, Form, Query


from ecos_backend.api.v1 import dependencies

from ecos_backend.api.v1.schemas import user as user_schemas
from ecos_backend.api.v1.schemas import moderation
from ecos_backend.api.v1.schemas import reception_point
from ecos_backend.api.v1.schemas import waste

from ecos_backend.service.moderation import ModerationService
from ecos_backend.service.user import UserService
from ecos_backend.service.reception_point import ReceptionPointService
from ecos_backend.service.waste import WasteService


user_create_schema = typing.Annotated[user_schemas.UserRequestCreateSchema, Form()]

moderation_create_schema = typing.Annotated[
    moderation.ModerationRequestCreateSchema, Form()
]

search_filter = typing.Annotated[typing.Optional[str], Query(alias="filter")]

user_service = typing.Annotated[UserService, Depends(dependencies.get_user_service)]

reception_point_service = typing.Annotated[
    ReceptionPointService, Depends(dependencies.get_reception_point_service)
]
waste_service = typing.Annotated[WasteService, Depends(dependencies.get_waste_service)]

moderation_service = typing.Annotated[
    ModerationService, Depends(dependencies.get_moderation_service)
]


data_request = typing.Annotated[
    tuple[dict | None, list[tuple[str, bytes, str]] | None],
    Depends(dependencies.parse_request),
]

verify_token = typing.Annotated[dict, Depends(dependencies.verify_token)]

reception_point_by_id = typing.Annotated[
    reception_point.ReceptionPointResponseSchema,
    Depends(dependencies.reception_point_by_id),
]
waste_by_id = typing.Annotated[
    waste.WasteResponseSchema, Depends(dependencies.waste_by_id)
]
