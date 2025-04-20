import abc

from sqlalchemy import Result, Select, func, select
from sqlalchemy.orm import joinedload

from ecos_backend.common.interfaces.repository import (
    T,
    AbstractRepository,
    AbstractSqlRepository,
)

from ecos_backend.db.models.user import User


class UserAbstractReposity(AbstractRepository[User], abc.ABC):
    @abc.abstractmethod
    async def get_by_verification_code(self, verification_code: str) -> User:
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_by_email(
        self, email: str, *, with_images: bool = False
    ) -> User | None:
        raise NotImplementedError()


class UserReposity(AbstractSqlRepository[User], UserAbstractReposity):
    async def get_by_verification_code(self, verification_code: str) -> T | None:
        stmt: Select = self._construct_get_by_verification_code_stmt(verification_code)
        result: Result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    def _construct_get_by_verification_code_stmt(
        self, verification_code: str
    ) -> Select:
        stmt: Select = select(self._model_cls).where(
            self._model_cls.verification_code == verification_code
        )
        return stmt

    async def get_by_email(
        self, email: str, *, with_images: bool = False
    ) -> User | None:
        stmt: Select = self._construct_get_by_email_stmt(email, with_images=with_images)
        result: Result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    def _construct_get_by_email_stmt(
        self, email: str, *, with_images: bool = False
    ) -> Select:
        stmt: Select[tuple[User]] = select(self._model_cls).where(
            func.lower(self._model_cls.email) == func.lower(email)
        )

        if with_images:
            stmt = stmt.options(joinedload(self._model_cls.user_image))

        return stmt
