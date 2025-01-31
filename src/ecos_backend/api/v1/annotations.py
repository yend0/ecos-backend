import typing

from fastapi import Depends, Form
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordRequestForm,
)

from ecos_backend.api.v1 import dependencies
from ecos_backend.api.v1.schemas import user as user_schemas
from ecos_backend.service.auth import AuthService
from ecos_backend.service.user import UserService

bearer_scheme = HTTPBearer()

user_create_schema = typing.Annotated[user_schemas.UserRequestCreateSchema, Form()]

credential_schema = typing.Annotated[
    HTTPAuthorizationCredentials, Depends(bearer_scheme)
]

request_form = typing.Annotated[OAuth2PasswordRequestForm, Depends()]


user_service = typing.Annotated[UserService, Depends(dependencies.get_user_service)]
auth_service = typing.Annotated[AuthService, Depends(dependencies.get_auth_service)]
