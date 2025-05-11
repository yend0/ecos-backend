import typing

from fastapi import Depends, Form


from ecos_backend.api.v1 import dependencies

from ecos_backend.api.v1.schemas import user as user_schemas
from ecos_backend.api.v1.schemas import reception_point
from ecos_backend.api.v1.schemas import waste
from ecos_backend.api.v1.schemas import waste_translation


from ecos_backend.service.user import UserService
from ecos_backend.service.reception_point import ReceptionPointService
from ecos_backend.service.waste import WasteService
from ecos_backend.service.waste_translation import WasteTranslationService


# Schema dependencies
user_create_schema = typing.Annotated[user_schemas.UserRequestCreateSchema, Form()]
waste_translation_create_schema = typing.Annotated[
    waste_translation.WasteTranslationRequestCreateSchema, Form()
]
waste_translation_update_schema = typing.Annotated[
    waste_translation.WasteTranslationRequestUpdatePartialSchema, Form()
]


# Service dependencies
user_service = typing.Annotated[UserService, Depends(dependencies.get_user_service)]
reception_point_service = typing.Annotated[
    ReceptionPointService, Depends(dependencies.get_reception_point_service)
]
waste_service = typing.Annotated[WasteService, Depends(dependencies.get_waste_service)]
waste_translation_service = typing.Annotated[
    WasteTranslationService, Depends(dependencies.get_waste_translation_service)
]

# Request dependencies
data_request = typing.Annotated[
    tuple[dict | None, list[tuple[str, bytes, str]] | None],
    Depends(dependencies.parse_request),
]

# Token dependencies
verify_token = typing.Annotated[dict, Depends(dependencies.verify_token)]


# Response by id dependencies
reception_point_by_id = typing.Annotated[
    reception_point.ReceptionPointResponseSchema,
    Depends(dependencies.reception_point_by_id),
]
waste_by_id = typing.Annotated[
    waste.WasteResponseSchema, Depends(dependencies.waste_by_id)
]
waste_translation_by_id = typing.Annotated[
    waste_translation.WasteTranslationResponseSchema,
    Depends(dependencies.waste_translation_by_id),
]
