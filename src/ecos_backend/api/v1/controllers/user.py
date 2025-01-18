import typing
import uuid

from fastapi import APIRouter, Depends, Form, status
from fastapi.security import HTTPAuthorizationCredentials

from keycloak.exceptions import KeycloakAuthenticationError


from ecos_backend.domain.user import UserModel
from ecos_backend.service.user import UserService
from ecos_backend.service.auth import AuthService
from ecos_backend.api.v1.dependencies import (
    get_user_service,
    get_auth_service,
    bearer_scheme,
)
from ecos_backend.api.v1.exception import UnauthorizedExcetion, NotFoundException
from ecos_backend.api.v1.schemas.user import UserRequestCreateSchema, UserResponseSchema


router = APIRouter()


@router.post(
    "/register",
    summary="Register user",
    response_description="User created successfully",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    user: typing.Annotated[UserRequestCreateSchema, Form()],
    user_service: typing.Annotated[UserService, Depends(get_user_service)],
) -> typing.Any:
    return await user_service.register_user(username=user.email, password=user.password)


@router.get(
    "/profile",
    summary="Get user profile",
    response_description="User profile retrieved successfully",
    response_model=UserResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_user(
    credentials: typing.Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    auth_service: typing.Annotated[AuthService, Depends(get_auth_service)],
    user_service: typing.Annotated[UserService, Depends(get_user_service)],
) -> typing.Any:
    try:
        sid: str = await auth_service.verify_token(credentials.credentials)
        if not sid:
            raise UnauthorizedExcetion(detail="Invalid token")

        user: UserModel | None = await user_service.get_account_information(
            uuid.UUID(sid)
        )

        if not user:
            raise NotFoundException(detail="User not found")

        return UserResponseSchema(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            birth_date=user.birth_date,
            image_url=user.image_url,
        )

    except KeycloakAuthenticationError:
        raise UnauthorizedExcetion(detail="Could not validate credentials")
