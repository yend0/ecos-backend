import typing

from fastapi import Depends, Form


from ecos_backend.api.v1 import dependencies
from ecos_backend.api.v1.schemas import user as user_schemas
from ecos_backend.service.user import UserService


user_create_schema = typing.Annotated[user_schemas.UserRequestCreateSchema, Form()]

user_service = typing.Annotated[UserService, Depends(dependencies.get_user_service)]

verify_token = typing.Annotated[dict, Depends(dependencies.verify_token)]
