import typing

from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from keycloak import KeycloakOpenID, KeycloakAdmin

from ecos_backend.db import s3_storage
from ecos_backend.db import database
from ecos_backend.common import config

from ecos_backend.common.keycloak_adapters import (
    KeycloakAdminAdapter,
    KeycloakClientAdapter,
)
from ecos_backend.common.unit_of_work import SQLAlchemyUnitOfWork, AbstractUnitOfWork
from ecos_backend.service.user import UserService
from ecos_backend.service.auth import AuthService

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


async def get_auth_service(
    keycloak_openid: typing.Annotated[KeycloakOpenID, Depends(client_adapter)],
) -> AuthService:
    return AuthService(client=keycloak_openid)
