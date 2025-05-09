import typing
import uuid

from fastapi import APIRouter, Request, status

from fastapi.responses import HTMLResponse
from jinja2 import Template
from starlette.requests import ClientDisconnect

from streaming_form_data.validators import ValidationError


from ecos_backend.common import config, enums, exception as custom_exceptions
from ecos_backend.common import validation

from ecos_backend.api.v1 import annotations
from ecos_backend.api.v1.schemas import user as user_schemas
from ecos_backend.api.v1.schemas.base import BaseInforamtionResponse
from ecos_backend.db.models.user import User


router = APIRouter()


@router.post(
    "/sign-up",
    summary="Register user",
    response_description="User created successfully",
    response_model=BaseInforamtionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    user: annotations.user_create_schema,
    user_service: annotations.user_service,
) -> typing.Any:
    await user_service.register_user(
        email=user.email,
        password=user.password,
    )

    return BaseInforamtionResponse(
        status=enums.Status.SUCCESS,
        message="User created successfully. Verification token successfully sent to your email.",
    )


@router.get(
    "/profile",
    summary="Get user profile",
    response_description="User profile retrieved successfully",
    response_model=user_schemas.UserResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_user(
    user_service: annotations.user_service,
    user_info: annotations.verify_token,
) -> typing.Any:
    sub = user_info["sub"]
    try:
        return await fetch_user(sub, user_service)
    except Exception as e:
        raise custom_exceptions.InternalServerException(detail=str(e))


@router.patch(
    "/profile",
    summary="Update user profile",
    response_description="User profile updated successfully",
    response_model=user_schemas.UserResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def update_user(
    user_service: annotations.user_service,
    user_info: annotations.verify_token,
    data_request: annotations.data_request,
) -> typing.Any:
    sub = user_info["sub"]

    try:
        data, uploaded_files = data_request

        if data:
            user_update_data: user_schemas.UserRequestUpdatePartialSchema = (
                parse_update_data(data)
            )
            user: User = await fetch_user(sub, user_service)
            user = update_user_model(user, user_update_data)

            if uploaded_files:
                updated_user: User = await user_service.update_account_information(
                    user=user,
                    file=uploaded_files[0][1],
                    file_extension=uploaded_files[0][2],
                )
            else:
                updated_user: User = await user_service.update_account_information(
                    user=user
                )

            return updated_user
        elif uploaded_files:
            user: User = await fetch_user(sub, user_service)
            await user_service.update_account_information(
                user=user,
                file=uploaded_files[0][1],
                file_extension=uploaded_files[0][2],
            )

            return await fetch_user(sub, user_service)

        else:
            user: User = await fetch_user(sub, user_service)

            return user
    except ClientDisconnect:
        pass
    except validation.MaxBodySizeException as e:
        MAX_REQUEST_BODY_SIZE = 1024 * 1024 * 10 + 1024
        raise custom_exceptions.PayloadTooLargeException(
            detail=f"Maximum request body size limit ({MAX_REQUEST_BODY_SIZE} bytes) exceeded ({e.body_len} bytes read)."
        )
    except ValidationError as e:
        raise custom_exceptions.ValidationException(detail=f"{str(e)}")
    except validation.InvalidFileTypeException as e:
        raise custom_exceptions.ValidationException(detail=f"{str(e)}")
    except Exception as e:
        raise custom_exceptions.InternalServerException(
            detail=f"There was an error uploading the file {e}"
        )


@router.get(
    "/verify-email/{token}",
    summary="Verify email",
    response_description="The email has been verified",
    status_code=status.HTTP_200_OK,
)
async def verify_email(
    token: str,
    user_service: annotations.user_service,
) -> typing.Any:
    result: bool = await user_service.verify_email(token=token)

    if not result:
        raise custom_exceptions.ForbiddenExcetion(
            detail="Invalid verification code or account already verified."
        )

    template: Template = config.env_jinja2.get_template("email_verified.html")
    html: str = template.render()
    return HTMLResponse(content=html, status_code=status.HTTP_200_OK)


@router.put(
    "/verify-email",
    summary="Resend verification email",
    response_description="Resend verification email",
    response_model=BaseInforamtionResponse,
    status_code=status.HTTP_200_OK,
)
async def resend_email(
    user_service: annotations.user_service,
    user_info: annotations.verify_token,
    request: Request,
) -> typing.Any:
    if user_info["email_verified"]:
        raise custom_exceptions.ForbiddenExcetion(detail="Account already verified.")

    sub = user_info["sub"]
    user: User | None = await user_service.get_account_information(uuid.UUID(sub))
    await user_service.resend_verification_email(email=user.email)

    return BaseInforamtionResponse(
        status=enums.Status.SUCCESS,
        message="Verification token successfully sent to your email.",
    )


def parse_update_data(data: dict) -> user_schemas.UserRequestUpdatePartialSchema:
    try:
        return user_schemas.UserRequestUpdatePartialSchema(**data)
    except ValidationError as e:
        raise custom_exceptions.ValidationException(detail=str(e))


async def fetch_user(sub: str, user_service: annotations.user_service) -> User:
    user: User | None = await user_service.get_account_information(uuid.UUID(sub))
    if not user:
        raise custom_exceptions.NotFoundException(detail="User not found.")
    return user


def update_user_model(
    user: User,
    update_data: user_schemas.UserRequestUpdatePartialSchema,
) -> User:
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    return user
