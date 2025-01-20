import typing
import uuid

from fastapi import APIRouter, Form, Query, status

from keycloak.exceptions import KeycloakAuthenticationError


from ecos_backend.domain.user import UserModel
from ecos_backend.api.v1.exception import UnauthorizedExcetion, NotFoundException
from ecos_backend.api.v1.dependencies import (
    user_service,
    auth_service,
    credential_schema,
)
from ecos_backend.api.v1.schemas.user import (
    UserRequestCreateSchema,
    UserRequestUpdatePartialSchema,
    UserResponseSchema,
)


user_create_schema = typing.Annotated[UserRequestCreateSchema, Form()]
user_update_partial_schema = typing.Annotated[UserRequestUpdatePartialSchema, Query()]

router = APIRouter()


@router.post(
    "/sign-up",
    summary="Register user",
    response_description="User created successfully",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    user: user_create_schema,
    user_service: user_service,
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
    credentials: credential_schema,
    auth_service: auth_service,
    user_service: user_service,
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


@router.patch(
    "/profile",
    summary="Update user profile",
    response_description="User profile updated successfully",
    response_model=UserResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def update_user(
    credentials: credential_schema,
    user_data: user_update_partial_schema,
    auth_service: auth_service,
    user_service: user_service,
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

        for field, value in user_data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)

        user_update: UserModel = await user_service.update_account_information(
            user=user
        )

        return UserResponseSchema(
            id=user_update.id,
            email=user_update.email,
            full_name=user_update.full_name,
            birth_date=user_update.birth_date,
            image_url=user_update.image_url,
        )

    except KeycloakAuthenticationError:
        raise UnauthorizedExcetion(detail="Could not validate credentials")
