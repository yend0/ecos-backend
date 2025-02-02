import typing

from fastapi import Depends, Security

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from keycloak import KeycloakAdmin

from ecos_backend.common.exception import ForbiddenExcetion, UnauthorizedExcetion
from ecos_backend.db import s3_storage
from ecos_backend.db import database
from ecos_backend.common import config

from ecos_backend.common.keycloak_adapters import (
    KeycloakAdminAdapter,
    KeycloakClientAdapter,
)
from ecos_backend.common.unit_of_work import SQLAlchemyUnitOfWork, AbstractUnitOfWork
from ecos_backend.service.user import UserService

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
