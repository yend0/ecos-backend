import abc
import uuid
import typing

from sqlalchemy import select, Select, Result
from sqlalchemy.ext.asyncio import AsyncSession

from ecos_backend.db.models.base import Base
from sqlalchemy import and_
from sqlalchemy.orm import Load, RelationshipProperty


T = typing.TypeVar("T", bound="Base")


class AbstractRepository(typing.Generic[T], abc.ABC):
    @abc.abstractmethod
    async def get_by_id(
        self, id: uuid.UUID, *, options: list[Load] | None = None
    ) -> T | None:
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_all(
        self,
        *,
        filters: dict[str, typing.Any] | None = None,
        options: list[Load] | None = None,
        limit: int | None = None,
        offset: int | None = None,
        order_by: list[typing.Any] | None = None,
    ) -> list[T]:
        raise NotImplementedError()

    @abc.abstractmethod
    async def add(self, record: T) -> T:
        raise NotImplementedError()

    @abc.abstractmethod
    async def delete(self, record: T) -> None:
        raise NotImplementedError()


class AbstractSqlRepository(AbstractRepository[T], abc.ABC):
    def __init__(self, session: AsyncSession, model_cls: typing.Type[T]) -> None:
        self._session: AsyncSession = session
        self._model_cls: type[T] = model_cls

    def _construct_get_stmt(
        self, id: uuid.UUID, options: list[Load] | None = None
    ) -> Select:
        stmt: Select[tuple[T]] = select(self._model_cls).where(self._model_cls.id == id)
        if options:
            stmt = stmt.options(*options)
        return stmt

    async def get_by_id(
        self, id: uuid.UUID, *, options: list[Load] | None = None
    ) -> T | None:
        stmt: Select = self._construct_get_stmt(id, options=options)
        result: Result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    def _construct_get_all_stmt(
        self,
        *,
        filters: dict[str, typing.Any] | None = None,
        options: list[Load] | None = None,
        limit: int | None = None,
        offset: int | None = None,
        order_by: list[typing.Any] | None = None,
    ) -> Select:
        stmt = select(self._model_cls)

        if filters:
            where_clauses = []
            for column, value in filters.items():
                if not hasattr(self._model_cls, column):
                    raise ValueError(f"Invalid column name {column}")

                if isinstance(value, (list, tuple)):
                    where_clauses.append(getattr(self._model_cls, column).in_(value))
                else:
                    where_clauses.append(getattr(self._model_cls, column) == value)

            if where_clauses:
                stmt: Select[tuple[T]] = stmt.where(and_(*where_clauses))

        if options:
            stmt = stmt.options(*options)

        if order_by:
            stmt = stmt.order_by(*order_by)

        if limit:
            stmt = stmt.limit(limit)

        if offset:
            stmt = stmt.offset(offset)

        return stmt

    async def get_all(
        self,
        *,
        filters: dict[str, typing.Any] | None = None,
        options: list[Load] | None = None,
        limit: int | None = None,
        offset: int | None = None,
        order_by: list[typing.Any] | None = None,
    ) -> list[T]:
        stmt: Select = self._construct_get_all_stmt(
            filters=filters,
            options=options,
            limit=limit,
            offset=offset,
            order_by=order_by,
        )
        result: Result = await self._session.execute(stmt)
        return result.scalars().all()

    async def add(self, record: T) -> T:
        self._session.add(record)
        await self._session.flush()
        await self._session.refresh(record)
        return record

    async def delete(self, record: T) -> None:
        await self._session.delete(record)
        await self._session.flush()

    def _construct_join_stmt(
        self,
        *,
        join_models: list[tuple[typing.Type[typing.Any], str]] | None = None,
        join_options: list[tuple[str, Load]] | None = None,
        filters: dict[str, typing.Any] | None = None,
        limit: int | None = None,
        offset: int | None = None,
        order_by: list[typing.Any] | None = None,
        join_type: str = "left",
    ) -> Select:
        """Constructs a join query statement.

        Args:
            join_models: List of tuples (model_class, relationship_attr)
            join_options: List of tuples (relationship_attr, load_option)
            filters: Dictionary of filters
            limit: Limit results
            offset: Offset results
            order_by: List of columns to order by
            join_type: Type of join ('left', 'inner', 'right', 'outer')
        """

        stmt: Select[tuple[T]] = select(self._model_cls)

        # Apply joins
        if join_models:
            for model, relationship_attr in join_models:
                if not hasattr(self._model_cls, relationship_attr):
                    raise ValueError(
                        f"Invalid relationship attribute {relationship_attr}"
                    )

                relationship = getattr(self._model_cls, relationship_attr)
                if not isinstance(relationship.property, RelationshipProperty):
                    raise ValueError(
                        f"{relationship_attr} is not a relationship attribute"
                    )

                join_method = {
                    "left": stmt.join_from,
                    "inner": stmt.join_from,
                    "right": stmt.join_from,  # Note: SQLAlchemy doesn't have direct right join
                    "outer": stmt.outerjoin_from,
                }.get(join_type.lower(), stmt.join_from)

                stmt = join_method(self._model_cls, model, relationship)

        # Apply eager loading options
        if join_options:
            options: list = []
            for relationship_attr, load_option in join_options:
                if not hasattr(self._model_cls, relationship_attr):
                    raise ValueError(
                        f"Invalid relationship attribute {relationship_attr}"
                    )
                options.append(load_option(getattr(self._model_cls, relationship_attr)))
            stmt = stmt.options(*options)

        # Apply filters
        if filters:
            where_clauses = []
            for column, value in filters.items():
                # Handle joined table filters with dot notation (e.g., "user.email")
                if "." in column:
                    table_name, column_name = column.split(".")
                    for model, relationship_attr in join_models or []:
                        if relationship_attr == table_name:
                            where_clauses.append(getattr(model, column_name) == value)
                            break
                    else:
                        raise ValueError(
                            f"Unknown joined table in filter: {table_name}"
                        )
                else:
                    if not hasattr(self._model_cls, column):
                        raise ValueError(f"Invalid column name {column}")
                    if isinstance(value, (list, tuple)):
                        where_clauses.append(
                            getattr(self._model_cls, column).in_(value)
                        )
                    else:
                        where_clauses.append(getattr(self._model_cls, column) == value)

            if where_clauses:
                stmt = stmt.where(and_(*where_clauses))

        # Apply ordering, limit, offset
        if order_by:
            stmt = stmt.order_by(*order_by)
        if limit:
            stmt = stmt.limit(limit)
        if offset:
            stmt = stmt.offset(offset)

        return stmt

    async def get_with_joins(
        self,
        *,
        join_models: list[tuple[typing.Type[typing.Any], str]] | None = None,
        join_options: list[tuple[str, Load]] | None = None,
        filters: dict[str, typing.Any] | None = None,
        limit: int | None = None,
        offset: int | None = None,
        order_by: list[typing.Any] | None = None,
        join_type: str = "left",
    ) -> list[T]:
        """Execute a join query and return results."""
        stmt: Select = self._construct_join_stmt(
            join_models=join_models,
            join_options=join_options,
            filters=filters,
            limit=limit,
            offset=offset,
            order_by=order_by,
            join_type=join_type,
        )
        result: Result = await self._session.execute(stmt)
        return result.scalars().all()
