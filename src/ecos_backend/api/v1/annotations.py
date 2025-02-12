import typing

from fastapi import Depends, Form


from ecos_backend.api.v1 import dependencies
from ecos_backend.api.v1.schemas import user as user_schemas
from ecos_backend.service.user import UserService
from ecos_backend.service.reception_point import ReceptionPointService


user_create_schema = typing.Annotated[user_schemas.UserRequestCreateSchema, Form()]

user_service = typing.Annotated[UserService, Depends(dependencies.get_user_service)]
reception_point_service = typing.Annotated[
    ReceptionPointService, Depends(dependencies.get_reception_point_service)
]

dict_file_extension = typing.Annotated[
    tuple[dict | None, bytes | None, str | None], Depends(dependencies.parse_request)
]

verify_token = typing.Annotated[dict, Depends(dependencies.verify_token)]
