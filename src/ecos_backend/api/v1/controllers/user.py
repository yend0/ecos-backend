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

from keycloak.exceptions import KeycloakAuthenticationError


from ecos_backend.domain import user as user_models
from ecos_backend.common import exception as custom_exceptions
from ecos_backend.common import validation

from ecos_backend.api.v1 import annotations
from ecos_backend.api.v1.schemas import user as user_schemas

MAX_FILE_SIZE = 1024 * 1024 * 10  # 10MB
MAX_REQUEST_BODY_SIZE = 1024 * 1024 * 10 + 1024


router = APIRouter()


@router.post(
    "/sign-up",
    summary="Register user",
    response_description="User created successfully",
    response_model=user_schemas.UserResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    user: annotations.user_create_schema,
    user_service: annotations.user_service,
) -> typing.Any:
    return await user_service.register_user(username=user.email, password=user.password)


@router.get(
    "/profile",
    summary="Get user profile",
    response_description="User profile retrieved successfully",
    response_model=user_schemas.UserResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_user(
    credentials: annotations.credential_schema,
    auth_service: annotations.auth_service,
    user_service: annotations.user_service,
) -> typing.Any:
    sid: str = await auth_service.verify_token(credentials.credentials)

    try:
        user: user_models.UserModel = await fetch_user(sid, user_service)
        return user_schemas.UserResponseSchema(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            birth_date=user.birth_date,
            image_url=user.image_url,
        )
    except KeycloakAuthenticationError:
        raise custom_exceptions.UnauthorizedExcetion(
            detail="Could not validate credentials"
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
    credentials: annotations.credential_schema,
    auth_service: annotations.auth_service,
    user_service: annotations.user_service,
    request: Request,
) -> typing.Any:
    sid: str = await auth_service.verify_token(credentials.credentials)

    try:
        data, file_bytes, file_extention = await parse_request(request)

        if data:
            user_update_data: user_schemas.UserRequestUpdatePartialSchema = (
                parse_update_data(data)
            )
            user: user_models.UserModel = await fetch_user(sid, user_service)
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
            user: user_models.UserModel = await fetch_user(sid, user_service)

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
            detail=f"Maximum request body size limit ({MAX_REQUEST_BODY_SIZE} bytes) exceeded ({e.body_len} bytes read)"
        )
    except ValidationError as e:
        raise custom_exceptions.ValidationException(detail=f"{str(e)}")
    except validation.InvalidFileTypeException as e:
        raise custom_exceptions.ValidationException(detail=f"{str(e)}")
    except Exception as e:
        raise custom_exceptions.InternalServerException(
            detail=f"There was an error uploading the file {e}"
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
    sid: str, user_service: annotations.user_service
) -> user_models.UserModel:
    user: user_models.UserModel | None = await user_service.get_account_information(
        uuid.UUID(sid)
    )
    if not user:
        raise custom_exceptions.NotFoundException(detail="User not found")
    return user


def update_user_model(
    user: user_models.UserModel,
    update_data: user_schemas.UserRequestUpdatePartialSchema,
) -> user_models.UserModel:
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    return user
