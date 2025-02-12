import abc


from ecos_backend.common.interfaces.repository import (
    AbstractRepository,
    AbstractSqlRepository,
)
from ecos_backend.domain.waste import WasteModel

from sqlalchemy.ext import asyncio


class WasteAbstractReposity(AbstractRepository[WasteModel]):
    @abc.abstractmethod
    async def delete(self, waste: WasteModel) -> None:
        raise NotImplementedError()


class WasteReposity(AbstractSqlRepository[WasteModel], WasteAbstractReposity):
    def __init__(self, session: asyncio.AsyncSession) -> None:
        super().__init__(session, WasteModel)

    async def delete(self, waste: WasteModel) -> None:
        await self._session.delete(waste)
        await self._session.commit()
