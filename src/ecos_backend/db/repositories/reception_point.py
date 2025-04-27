import abc
import uuid

from sqlalchemy.orm import selectinload

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


class ReceptionPointReposity(
    AbstractSqlRepository[ReceptionPoint], ReceptionPointAbstractReposity
):
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
