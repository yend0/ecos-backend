import json
import typing

from urllib.parse import unquote
import uuid

from fastapi import Depends, Path, Security, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from sqlalchemy.ext.asyncio import AsyncSession

from keycloak import KeycloakAdmin

from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import ValueTarget


from ecos_backend.api.v1.schemas.waste import WasteResponseSchema
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

from ecos_backend.models.reception_point import ReceptionPointDTO
from ecos_backend.models.waste import WasteDTO
from ecos_backend.service.user import UserService
from ecos_backend.service.reception_point import ReceptionPointService
from ecos_backend.service.waste import WasteService

from ecos_backend.api.v1.schemas.reception_point import ReceptionPointResponseSchema

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


async def get_waste_service(
    uow: typing.Annotated[AbstractUnitOfWork, Depends(get_uow)],
    s3: typing.Annotated[s3_storage.Boto3DAO, Depends(s3_client)],
) -> UserService:
    return WasteService(uow=uow, s3_storage=s3)


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
) -> tuple[dict | None, list[tuple[str, bytes, str]] | None]:
    body_validator = validation.MaxBodySizeValidator(const.MAX_REQUEST_BODY_SIZE)
    data = ValueTarget()
    parser = StreamingFormDataParser(headers=request.headers)

    file_targets: dict = {}

    filenames_header: str | None = request.headers.get("filenames")
    filenames: list[str] = (
        [unquote(f.strip()) for f in filenames_header.split(",")]
        if filenames_header
        else []
    )

    for filename in filenames:
        file_target = validation.BytesTarget(
            validator=validation.MaxSizeValidator(const.MAX_FILE_SIZE)
        )
        parser.register(filename, file_target)
        file_targets[filename] = file_target

    parser.register("data", data)

    async for chunk in request.stream():
        body_validator(chunk)
        parser.data_received(chunk)

    try:
        raw_data: str | None = data.value.decode() if data.value else None
        if raw_data and raw_data.startswith('"') and raw_data.endswith('"'):
            raw_data = raw_data[1:-1].replace('\\"', '"')
        data_dict: dict | None = json.loads(raw_data) if raw_data else None
    except json.JSONDecodeError as e:
        raise custom_exceptions.ValidationException(
            detail=f"Invalid JSON format: {str(e)}"
        )

    uploaded_files: list = []
    for filename, file_target in file_targets.items():
        if file_target.content:
            try:
                file_extension: str = validation.FileTypeValidator.validate(
                    file_target.content
                ).lstrip(".")
                uploaded_files.append((filename, file_target.content, file_extension))
            except validation.InvalidFileTypeException as e:
                raise custom_exceptions.ValidationException(detail=str(e))

    return data_dict, uploaded_files


async def reception_point_by_id(
    reception_point_id: typing.Annotated[uuid.UUID, Path],
    reception_point_service: typing.Annotated[
        ReceptionPointService, Depends(get_reception_point_service)
    ],
) -> ReceptionPointResponseSchema:
    reception_point: (
        ReceptionPointDTO | None
    ) = await reception_point_service.get_reception_point_by_id(reception_point_id)

    if reception_point is None:
        raise custom_exceptions.NotFoundException(
            detail=f"Reception point with ${reception_point_id} id not found."
        )

    return ReceptionPointResponseSchema(
        **await reception_point.to_dict(exclude={"images_url"})
    )


async def waste_by_id(
    waste_id: typing.Annotated[uuid.UUID, Path],
    waste_service: typing.Annotated[WasteService, Depends(get_waste_service)],
) -> ReceptionPointResponseSchema:
    waste: WasteDTO | None = await waste_service.get_waste_by_id(waste_id)

    if waste is None:
        raise custom_exceptions.NotFoundException(
            detail=f"Waste with ${waste_id} id not found."
        )

    return WasteResponseSchema(**await waste.to_dict())
