import typing

from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from keycloak import KeycloakOpenID, KeycloakAdmin

from ecos_backend.db.database import dbSQLHelper
from ecos_backend.common.keycloak_adapters import (
    KeycloakAdminAdapter,
    KeycloakClientAdapter,
)

from ecos_backend.common.unit_of_work import SQLAlchemyUnitOfWork, AbstractUnitOfWork
from ecos_backend.service.user import UserService
from ecos_backend.service.auth import AuthService

admin_adapter = KeycloakAdminAdapter()
client_adapter = KeycloakClientAdapter()


async def get_uow(
    session: typing.Annotated[AsyncSession, Depends(dbSQLHelper.session_dependency)],
) -> typing.AsyncGenerator[AbstractUnitOfWork, None]:
    async with SQLAlchemyUnitOfWork(session) as uow:
        yield uow


async def get_user_service(
    uow: typing.Annotated[AbstractUnitOfWork, Depends(get_uow)],
    admin: typing.Annotated[KeycloakAdmin, Depends(admin_adapter)],
) -> UserService:
    return UserService(uow=uow, admin=admin)


async def get_auth_service(
    keycloak_openid: typing.Annotated[KeycloakOpenID, Depends(client_adapter)],
) -> AuthService:
    return AuthService(client=keycloak_openid)
