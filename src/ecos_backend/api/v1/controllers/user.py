import typing

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ecos_backend.api.v1.dependencies import get_user_service
from ecos_backend.api.v1.schemas.user import UserRequestCreateSchema, UserResponseSchema
from ecos_backend.service.user import UserService

router = APIRouter()

bearer_scheme = HTTPBearer()


@router.get(
    "/",
    response_model=UserResponseSchema,
)
async def get_user(
    credentials: typing.Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    user_service: typing.Annotated[UserService, Depends(get_user_service)],
) -> typing.Any:
    return await user_service.get_account_information(credentials.credentials)


@router.post(
    "/",
    summary="Register user",
    response_description="User created successfully",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def add_user(
    user: UserRequestCreateSchema,
    user_service: typing.Annotated[UserService, Depends(get_user_service)],
) -> typing.Any:
    return await user_service.register_user(user)
