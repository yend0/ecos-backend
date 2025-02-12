import abc
import uuid
import typing

from operator import and_

from sqlalchemy import select, Select, Result
from sqlalchemy.ext.asyncio import AsyncSession

from ecos_backend.common.interfaces import model


T = typing.TypeVar("T", bound=model.AbstractModel)


class AbstractRepository(typing.Generic[T], abc.ABC):
    @abc.abstractmethod
    async def get_by_id(self, id: uuid.UUID) -> typing.Optional[T]:
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_all(self, **filters) -> list[T]:
        raise NotImplementedError()

    @abc.abstractmethod
    async def add(self, record: T) -> T:
        raise NotImplementedError()


class AbstractSqlRepository(AbstractRepository[T], abc.ABC):
    def __init__(self, session: AsyncSession, model_cls: typing.Type[T]) -> None:
        super().__init__()

        self._session: AsyncSession = session
        self._model_cls: type[T] = model_cls

    def _construct_get_stmt(self, id: int) -> Select:
        stmt: Select = select(self._model_cls).where(self._model_cls.id == id)
        return stmt

    async def get_by_id(self, id: uuid.UUID) -> typing.Optional[T]:
        stmt: Select = self._construct_get_stmt(id)
        result: Result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    def _construct_get_all_stmt(self, **filters) -> Select:
        stmt: Select = select(self._model_cls)
        where_clauses: list = []

        for c, v in filters.items():
            if not hasattr(self._model_cls, c):
                raise ValueError(f"Invalid column name {c}")
            where_clauses.append(getattr(self._model_cls, c) == v)

        if len(where_clauses) == 1:
            stmt = stmt.where(where_clauses[0])
        elif len(where_clauses) > 1:
            stmt = stmt.where(and_(*where_clauses))
        return stmt

    async def get_all(self, **filters) -> list[T]:
        stmt: Select = self._construct_get_all_stmt(**filters)
        result: Result = await self._session.execute(stmt)
        return result.scalars().all()

    async def add(self, record: T) -> T:
        self._session.add(record)
        await self._session.flush()
        await self._session.refresh(record)
        return record
