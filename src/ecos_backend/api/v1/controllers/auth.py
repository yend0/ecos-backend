import hashlib
import typing

from fastapi import APIRouter, status

from ecos_backend.api.v1 import annotations
from ecos_backend.api.v1.schemas.base import BaseInforamtionResponse
from ecos_backend.api.v1.schemas.token import TokenResponse
from ecos_backend.common.exception import ForbiddenExcetion

router = APIRouter()


@router.post(
    "/sign-in",
    summary="Login user",
    response_description="The user has successfully logged in",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def login(
    form_data: annotations.request_form,
    auth_service: annotations.auth_service,
) -> typing.Any:
    json_data: dict[str, str | int] = await auth_service.auth(
        form_data.username, form_data.password
    )

    return TokenResponse(**json_data)


@router.post(
    "/sign-out",
    summary="Logout user",
    response_description="The user has successfully logged out",
    response_model=BaseInforamtionResponse,
    status_code=status.HTTP_200_OK,
)
async def logout(
    credentials: annotations.credential_schema,
    auth_service: annotations.auth_service,
) -> typing.Any:
    await auth_service.logout(credentials.credentials)

    return BaseInforamtionResponse(
        status="success",
        message="User logged out successfully",
    )


@router.post(
    "/token/refresh",
    summary="Refresh token",
    response_description="The token has been refreshed",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def refresh_token(
    credentials: annotations.credential_schema,
    auth_service: annotations.auth_service,
) -> TokenResponse:
    json_data: dict[str, str | int] = await auth_service.refresh_token(
        credentials.credentials
    )

    return TokenResponse(**json_data)


@router.get(
    "/verify-email/{token}",
    summary="Verify email",
    response_description="The email has been verified",
    response_model=BaseInforamtionResponse,
    status_code=status.HTTP_200_OK,
)
async def verify_email(
    token: str,
    user_service: annotations.user_service,
) -> typing.Any:
    verification_code: str = compute_verification_code_from_token(token)

    result: bool = await user_service.verify_email(verification_code)

    if not result:
        raise ForbiddenExcetion(
            detail="Invalid verification code or account already verified"
        )

    return BaseInforamtionResponse(
        status="success",
        message="Account verified successfully",
    )


def compute_verification_code_from_token(token) -> str:
    hashedCode: hashlib._Hash = hashlib.sha256()
    hashedCode.update(bytes.fromhex(token))
    verification_code: str = hashedCode.hexdigest()
    return verification_code
