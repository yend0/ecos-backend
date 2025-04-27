import abc
import typing
import uuid

from sqlalchemy import Function, Result, Select, and_, select, func
from sqlalchemy.orm import selectinload
from geoalchemy2.functions import ST_DWithin

from ecos_backend.db.models.reception_point import ReceptionPoint
from ecos_backend.db.models.waste import Waste

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

        stmt = select(self._model_cls)

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
        reception_point: ReceptionPoint | None = await self._session.get(
            ReceptionPoint,
            reception_point_id,
            options=[selectinload(ReceptionPoint.wastes)],
        )

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
