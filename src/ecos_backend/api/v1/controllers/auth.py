import typing

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm


from ecos_backend.api.v1.dependencies import auth_service, credential_schema
from ecos_backend.api.v1.exception import UnauthorizedExcetion
from ecos_backend.api.v1.schemas.token import TokenResponse

request_form = typing.Annotated[OAuth2PasswordRequestForm, Depends()]

router = APIRouter()


@router.post(
    "/sign-in",
    summary="Login user",
    response_description="The user has successfully logged in",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def login(
    form_data: request_form,
    auth_service: auth_service,
) -> typing.Any:
    json_data: dict[str, str | int] = await auth_service.auth(
        form_data.username, form_data.password
    )

    if not json_data:
        raise UnauthorizedExcetion(detail="Invalid username or password")

    return TokenResponse(**json_data)


@router.post(
    "/sign-out",
    summary="Logout user",
    response_description="The user has successfully logged out",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    credentials: credential_schema,
    auth_service: auth_service,
) -> None:
    await auth_service.logout(credentials.credentials)


@router.post(
    "/token/refresh",
    summary="Refresh token",
    response_description="The token has been refreshed",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def refresh_token(
    credentials: credential_schema,
    auth_service: auth_service,
) -> TokenResponse:
    json_data: dict[str, str | int] = await auth_service.refresh_token(
        credentials.credentials
    )

    if not json_data:
        raise UnauthorizedExcetion(detail="Could not refresh token")

    return TokenResponse(**json_data)
