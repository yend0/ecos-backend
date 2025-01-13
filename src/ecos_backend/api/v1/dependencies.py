import typing

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ecos_backend.db.database import dbSQLHelper
from ecos_backend.common.unit_of_work import SQLAlchemyUnitOfWork, AbstractUnitOfWork
from ecos_backend.service.user import UserService


async def get_uow(
    session: typing.Annotated[
        AsyncSession, Depends(dbSQLHelper.scoped_session_dependency)
    ],
) -> typing.AsyncGenerator[AbstractUnitOfWork, None]:
    async with SQLAlchemyUnitOfWork(session) as uow:
        yield uow


def get_user_service(
    uow: typing.Annotated[AbstractUnitOfWork, Depends(get_uow)],
) -> UserService:
    return UserService(uow)
