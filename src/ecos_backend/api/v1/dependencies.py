import typing

from fastapi import Depends
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from keycloak import KeycloakOpenID, KeycloakAdmin

from ecos_backend.db.database import dbSQLHelper
from ecos_backend.common.keycloak_client_config import get_keycloak_openid
from ecos_backend.common.keycloak_admin_config import get_keycloak_admin

from ecos_backend.common.unit_of_work import SQLAlchemyUnitOfWork, AbstractUnitOfWork
from ecos_backend.service.user import UserService
from ecos_backend.service.auth import AuthService


bearer_scheme = HTTPBearer()


async def get_uow(
    session: typing.Annotated[
        AsyncSession, Depends(dbSQLHelper.scoped_session_dependency)
    ],
) -> typing.AsyncGenerator[AbstractUnitOfWork, None]:
    async with SQLAlchemyUnitOfWork(session) as uow:
        yield uow


async def get_user_service(
    uow: typing.Annotated[AbstractUnitOfWork, Depends(get_uow)],
    admin: typing.Annotated[KeycloakAdmin, Depends(get_keycloak_admin)],
) -> UserService:
    return UserService(uow=uow, admin=admin)


async def get_auth_service(
    keycloak_openid: typing.Annotated[KeycloakOpenID, Depends(get_keycloak_openid)],
) -> AuthService:
    return AuthService(client=keycloak_openid)
