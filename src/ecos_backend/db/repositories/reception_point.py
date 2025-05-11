import abc
import typing
import uuid

from sqlalchemy import Function, Result, Select, and_, select, func
from sqlalchemy.orm import selectinload
from geoalchemy2.functions import ST_DWithin

from ecos_backend.db.models.reception_point import ReceptionPoint
from ecos_backend.db.models.waste import Waste
from ecos_backend.db.models.user import User

from ecos_backend.common.interfaces.repository import (
    AbstractRepository,
    AbstractSqlRepository,
)


class ReceptionPointAbstractReposity(AbstractRepository[ReceptionPoint], abc.ABC):
    @abc.abstractmethod
    async def add_waste_type(
        self, reception_point_id: uuid.UUID, waste_id: uuid.UUID
    ) -> ReceptionPoint:
        raise NotImplementedError()

    @abc.abstractmethod
    async def delete_waste_type(
        self, reception_point_id: uuid.UUID, waste_id: uuid.UUID
    ) -> ReceptionPoint:
        raise NotImplementedError()

    @abc.abstractmethod
    async def add_user(
        self, reception_point_id: uuid.UUID, user_id: uuid.UUID
    ) -> ReceptionPoint:
        raise NotImplementedError()

    @abc.abstractmethod
    async def delete_user(
        self, reception_point_id: uuid.UUID, user_id: uuid.UUID
    ) -> ReceptionPoint:
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_nearby_points(
        self,
        user_lat: float,
        user_lon: float,
        radius_meters: float,
        filters: dict[str, typing.Any] | None = None,
        page: int = 1,
        per_page: int = 10,
        options: list | None = None,
    ) -> list[ReceptionPoint]:
        raise NotImplementedError()


class ReceptionPointReposity(
    AbstractSqlRepository[ReceptionPoint], ReceptionPointAbstractReposity
):
    async def get_nearby_points(
        self,
        user_lat: float,
        user_lon: float,
        radius_meters: float,
        filters: dict[str, typing.Any] | None = None,
        page: int = 1,
        per_page: int = 10,
        options: list | None = None,
    ) -> list[ReceptionPoint]:
        point: Function[typing.Any] = func.ST_SetSRID(
            func.ST_MakePoint(user_lon, user_lat), 4326
        )

        ReceptionPoint = self._model_cls
        stmt = select(ReceptionPoint).distinct()

        waste_type_id = None
        if filters and "waste_type" in filters:
            waste_type_id = filters.pop("waste_type")
            stmt = stmt.join(ReceptionPoint.wastes)
            stmt = stmt.where(Waste.id == waste_type_id)

        if filters:
            where_clauses: list = []
            for column, value in filters.items():
                if not hasattr(self._model_cls, column):
                    raise ValueError(f"Invalid column name {column}")
                if isinstance(value, (list, tuple)):
                    where_clauses.append(getattr(self._model_cls, column).in_(value))
                else:
                    where_clauses.append(getattr(self._model_cls, column) == value)
            if where_clauses:
                stmt: Select[tuple[ReceptionPoint]] = stmt.where(and_(*where_clauses))

        stmt = stmt.where(ST_DWithin(self._model_cls.location, point, radius_meters))

        if options:
            stmt = stmt.options(*options)

        stmt = stmt.limit(per_page).offset((page - 1) * per_page)

        result: Result[tuple[ReceptionPoint]] = await self._session.execute(stmt)
        return result.scalars().all()

    async def add_waste_type(
        self, reception_point_id: uuid.UUID, waste_id: uuid.UUID
    ) -> ReceptionPoint:
        stmt = (
            select(ReceptionPoint)
            .options(selectinload(ReceptionPoint.wastes))
            .where(ReceptionPoint.id == reception_point_id)
        )
        result = await self._session.execute(stmt)
        reception_point = result.scalar_one_or_none()

        waste: Waste | None = await self._session.get(Waste, waste_id)

        if not reception_point or not waste:
            raise ValueError("ReceptionPoint or Waste not found")

        if waste not in reception_point.wastes:
            reception_point.wastes.append(waste)
            await self._session.flush()

        return reception_point

    async def delete_waste_type(
        self, reception_point_id: uuid.UUID, waste_id: uuid.UUID
    ) -> ReceptionPoint:
        reception_point: ReceptionPoint | None = await self._session.get(
            ReceptionPoint,
            reception_point_id,
            options=[selectinload(ReceptionPoint.wastes)],
        )

        waste: Waste | None = await self._session.get(Waste, waste_id)

        if not reception_point or not waste:
            raise ValueError("ReceptionPoint or Waste not found")

        if waste in reception_point.wastes:
            reception_point.wastes.remove(waste)
            await self._session.flush()

        return reception_point

    async def add_user(
        self, reception_point_id: uuid.UUID, user_id: uuid.UUID
    ) -> ReceptionPoint:
        stmt = (
            select(ReceptionPoint)
            .options(selectinload(ReceptionPoint.users))
            .where(ReceptionPoint.id == reception_point_id)
        )
        result = await self._session.execute(stmt)
        reception_point = result.scalar_one_or_none()

        user: User | None = await self._session.get(User, user_id)

        reception_point.users.append(user)
        await self._session.flush()

        return reception_point

    async def delete_user(
        self, reception_point_id: uuid.UUID, user_id: uuid.UUID
    ) -> ReceptionPoint:
        reception_point: ReceptionPoint | None = await self._session.get(
            ReceptionPoint,
            reception_point_id,
            options=[selectinload(ReceptionPoint.users)],
        )

        user: User | None = await self._session.get(User, user_id)

        if not reception_point or not user:
            raise ValueError("ReceptionPoint or User not found")

        if user in reception_point.users:
            reception_point.users.remove(user)
            await self._session.flush()

        return reception_point
