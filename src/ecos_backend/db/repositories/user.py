import abc
import uuid

from sqlalchemy import Result, Select, and_, select

from ecos_backend.common.interfaces.repository import (
    AbstractRepository,
    AbstractSqlRepository,
)

from ecos_backend.models.user import UserModel

from ecos_backend.db.adapters import orm


class UserAbstractReposity(AbstractRepository, abc.ABC):
    @abc.abstractmethod
    async def get_by_verification_code(self, verification_code: str) -> UserModel:
        raise NotImplementedError()


class UserReposity(AbstractSqlRepository, UserAbstractReposity):
    async def get_by_id(self, id: uuid.UUID) -> UserModel | None:
        stmt: Select = self._construct_get_stmt(id)
        result: Result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_verification_code(
        self, verification_code: str
    ) -> UserModel | None:
        stmt: Select = self._construct_get_by_verification_code_stmt(verification_code)
        result: Result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, **filters) -> list[UserModel]:
        stmt: Select = self._construct_get_all_stmt(**filters)
        result: Result = await self._session.execute(stmt)
        return result.scalars().all()

    async def add(self, model: UserModel) -> UserModel:
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return model

    async def delete(self, id: uuid.UUID) -> None:
        raise NotImplementedError()

    def _construct_get_by_verification_code_stmt(
        self, verification_code: str
    ) -> Select:
        stmt: Select = select(UserModel).where(
            orm.user_table.c.verification_code == verification_code
        )
        return stmt

    def _construct_get_stmt(self, id: int) -> Select:
        stmt: Select = select(UserModel).where(orm.user_table.c.id == id)
        return stmt

    def _construct_get_all_stmt(self, **filters) -> Select:
        stmt: Select = select(UserModel)
        where_clauses: list = []

        for c, v in filters.items():
            if not hasattr(orm.user_table.c, c):
                raise ValueError(f"Invalid column name {c}")
            where_clauses.append(getattr(orm.user_table.c, c) == v)

        if len(where_clauses) == 1:
            stmt = stmt.where(where_clauses[0])
        elif len(where_clauses) > 1:
            stmt = stmt.where(and_(*where_clauses))
        return stmt
