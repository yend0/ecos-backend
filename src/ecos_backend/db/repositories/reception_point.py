import abc


from ecos_backend.common.interfaces.repository import (
    AbstractRepository,
    AbstractSqlRepository,
)
from ecos_backend.models.reception_point import ReceptionPointDTO

from sqlalchemy.ext import asyncio


class ReceptionPointAbstractReposity(AbstractRepository[ReceptionPointDTO]):
    @abc.abstractmethod
    async def delete(self, reception_point: ReceptionPointDTO) -> None:
        raise NotImplementedError()


class ReceptionPointReposity(
    AbstractSqlRepository[ReceptionPointDTO], ReceptionPointAbstractReposity
):
    def __init__(self, session: asyncio.AsyncSession) -> None:
        super().__init__(session, ReceptionPointDTO)

    async def delete(self, reception_point: ReceptionPointDTO) -> None:
        await self._session.delete(reception_point)
        await self._session.commit()
