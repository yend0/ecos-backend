import os
import json
import typing

from urllib.parse import unquote

from fastapi import Depends, Security, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from sqlalchemy.ext.asyncio import AsyncSession

from keycloak import KeycloakAdmin

from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import ValueTarget
from streaming_form_data.validators import MaxSizeValidator


from ecos_backend.db import s3_storage
from ecos_backend.db import database
from ecos_backend.common import config
from ecos_backend.common import validation
from ecos_backend.common import constatnts as const
from ecos_backend.common import exception as custom_exceptions
from ecos_backend.common.exception import ForbiddenExcetion, UnauthorizedExcetion
from ecos_backend.common.unit_of_work import SQLAlchemyUnitOfWork, AbstractUnitOfWork
from ecos_backend.common.keycloak_adapters import (
    KeycloakAdminAdapter,
    KeycloakClientAdapter,
)

from ecos_backend.service.user import UserService
from ecos_backend.service.reception_point import ReceptionPointService


bearer_scheme = HTTPBearer()

admin_adapter = KeycloakAdminAdapter()
client_adapter = KeycloakClientAdapter()
database_client: database.Database = database.database_factory(
    config=config.database_config
)
s3_client: s3_storage.Boto3DAO = s3_storage.s3_bucket_factory(config=config.s3_config)


async def get_uow(
    session: typing.Annotated[
        AsyncSession, Depends(database_client.session_dependency)
    ],
) -> typing.AsyncGenerator[AbstractUnitOfWork, None]:
    async with SQLAlchemyUnitOfWork(session) as uow:
        yield uow


async def get_user_service(
    uow: typing.Annotated[AbstractUnitOfWork, Depends(get_uow)],
    admin: typing.Annotated[KeycloakAdmin, Depends(admin_adapter)],
    s3: typing.Annotated[s3_storage.Boto3DAO, Depends(s3_client)],
) -> UserService:
    return UserService(uow=uow, admin=admin, s3_storage=s3)


async def get_reception_point_service(
    uow: typing.Annotated[AbstractUnitOfWork, Depends(get_uow)],
    s3: typing.Annotated[s3_storage.Boto3DAO, Depends(s3_client)],
) -> UserService:
    return ReceptionPointService(uow=uow, s3_storage=s3)


async def verify_token(
    credentials: typing.Annotated[
        HTTPAuthorizationCredentials, Security(bearer_scheme)
    ],
):
    token: str = credentials.credentials
    try:
        user_info = await client_adapter.openid.a_userinfo(token)
        if not user_info or "sub" not in user_info:
            raise UnauthorizedExcetion(detail="Invalid token")
        return user_info
    except Exception as e:
        print(f"Error: {str(e)}")
        raise ForbiddenExcetion(detail="Invalid or expired token")


async def parse_request(
    request: Request,
) -> tuple[dict | None, bytes | None, str | None]:
    body_validator = validation.MaxBodySizeValidator(const.MAX_REQUEST_BODY_SIZE)
    data = ValueTarget()
    filename = request.headers.get("filename")
    parser = StreamingFormDataParser(headers=request.headers)

    file_target = None
    if filename:
        filename: str = unquote(filename)
        file_target = validation.BytesTarget(
            validator=MaxSizeValidator(const.MAX_FILE_SIZE)
        )
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
    else:
        return data_dict, None, None
