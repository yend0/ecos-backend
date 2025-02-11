import abc
import typing

from sqlalchemy import Result, Select, select

from ecos_backend.common.interfaces.repository import (
    T,
    AbstractRepository,
    AbstractSqlRepository,
)
from ecos_backend.domain.user import UserModel

from sqlalchemy.ext import asyncio


class UserAbstractReposity(AbstractRepository[UserModel]):
    @abc.abstractmethod
    async def get_by_verification_code(self, verification_code: str) -> UserModel:
        raise NotImplementedError()


class UserReposity(AbstractSqlRepository[UserModel], UserAbstractReposity):
    def __init__(self, session: asyncio.AsyncSession) -> None:
        super().__init__(session, UserModel)

    def _construct_get_by_verification_code_stmt(
        self, verification_code: str
    ) -> Select:
        stmt: Select = select(self._model_cls).where(
            self._model_cls.verification_code == verification_code
        )
        return stmt

    async def get_by_verification_code(
        self, verification_code: str
    ) -> typing.Optional[T]:
        stmt: Select = self._construct_get_by_verification_code_stmt(verification_code)
        result: Result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
