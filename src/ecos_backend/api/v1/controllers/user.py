import os
import json
import typing
import uuid

from urllib.parse import unquote

from fastapi import APIRouter, Request, status

from starlette.requests import ClientDisconnect

from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import ValueTarget
from streaming_form_data.validators import MaxSizeValidator, ValidationError


from ecos_backend.domain import user as user_models
from ecos_backend.common import exception as custom_exceptions
from ecos_backend.common import validation

from ecos_backend.api.v1 import annotations
from ecos_backend.api.v1.schemas import user as user_schemas
from ecos_backend.api.v1.schemas.base import BaseInforamtionResponse

MAX_FILE_SIZE = 1024 * 1024 * 10  # 10MB
MAX_REQUEST_BODY_SIZE = 1024 * 1024 * 10 + 1024


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
    request: Request,
) -> typing.Any:
    await user_service.register_user(
        username=user.email,
        password=user.password,
        request=request,
    )

    return BaseInforamtionResponse(
        status="success",
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
        user: user_models.UserModel = await fetch_user(sub, user_service)
        return user_schemas.UserResponseSchema(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            birth_date=user.birth_date,
            image_url=user.image_url,
        )
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
    request: Request,
) -> typing.Any:
    sub = user_info["sub"]

    try:
        data, file_bytes, file_extention = await parse_request(request)

        if data:
            user_update_data: user_schemas.UserRequestUpdatePartialSchema = (
                parse_update_data(data)
            )
            user: user_models.UserModel = await fetch_user(sub, user_service)
            user = update_user_model(user, user_update_data)
            updated_user: user_models.UserModel = (
                await user_service.update_account_information(
                    user=user, file=file_bytes, file_extention=file_extention
                )
            )

            return user_schemas.UserResponseSchema(
                id=updated_user.id,
                email=updated_user.email,
                full_name=updated_user.full_name,
                birth_date=updated_user.birth_date,
                image_url=updated_user.image_url,
            )
        else:
            user: user_models.UserModel = await fetch_user(sub, user_service)

            return user_schemas.UserResponseSchema(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                birth_date=user.birth_date,
                image_url=user.image_url,
            )
    except ClientDisconnect:
        pass
    except validation.MaxBodySizeException as e:
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
    response_model=BaseInforamtionResponse,
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

    return BaseInforamtionResponse(
        status="success",
        message="Account verified successfully.",
    )


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
    await user_service.resend_verification_email(id=uuid.UUID(sub), request=request)

    return BaseInforamtionResponse(
        status="success",
        message="Verification token successfully sent to your email.",
    )


async def parse_request(
    request: Request,
) -> tuple[dict | None, bytes | None, str | None]:
    body_validator = validation.MaxBodySizeValidator(MAX_REQUEST_BODY_SIZE)
    data = ValueTarget()
    filename = request.headers.get("filename")
    parser = StreamingFormDataParser(headers=request.headers)

    file_target = None
    if filename:
        filename: str = unquote(filename)
        file_target = validation.BytesTarget(validator=MaxSizeValidator(MAX_FILE_SIZE))
        parser.register("file", file_target)

    parser.register("data", data)

    async for chunk in request.stream():
        body_validator(chunk)
        parser.data_received(chunk)

    data_dict: os.Any | None = json.loads(data.value.decode()) if data.value else None
    file_bytes: bytes | None = file_target.content if file_target else None

    if file_bytes:
        try:
            file_extension: str = validation.FileTypeValidator.validate(
                file_bytes
            ).lstrip(".")
        except validation.InvalidFileTypeException as e:
            raise custom_exceptions.ValidationException(detail=str(e))

    return data_dict, file_bytes, file_extension


def parse_update_data(data: dict) -> user_schemas.UserRequestUpdatePartialSchema:
    try:
        return user_schemas.UserRequestUpdatePartialSchema(**data)
    except ValidationError as e:
        raise custom_exceptions.ValidationException(detail=str(e))


async def fetch_user(
    sub: str, user_service: annotations.user_service
) -> user_models.UserModel:
    user: user_models.UserModel | None = await user_service.get_account_information(
        uuid.UUID(sub)
    )
    if not user:
        raise custom_exceptions.NotFoundException(detail="User not found.")
    return user


def update_user_model(
    user: user_models.UserModel,
    update_data: user_schemas.UserRequestUpdatePartialSchema,
) -> user_models.UserModel:
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    return user
