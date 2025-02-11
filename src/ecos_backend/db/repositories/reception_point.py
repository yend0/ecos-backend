import abc


from ecos_backend.common.interfaces.repository import (
    AbstractRepository,
    AbstractSqlRepository,
)
from ecos_backend.domain.reception_point import ReceptionPointModel

from sqlalchemy.ext import asyncio


class ReceptionPointAbstractReposity(AbstractRepository[ReceptionPointModel], abc.ABC):
    @abc.abstractmethod
    async def delete(self, reception_point: ReceptionPointModel) -> None:
        raise NotImplementedError()


class ReceptionPointReposity(
    AbstractSqlRepository[ReceptionPointModel], ReceptionPointAbstractReposity
):
    def __init__(self, session: asyncio.AsyncSession) -> None:
        super().__init__(session, ReceptionPointModel)

    async def delete(self, reception_point: ReceptionPointModel) -> None:
        await self._session.delete(reception_point)
        await self._session.commit()
