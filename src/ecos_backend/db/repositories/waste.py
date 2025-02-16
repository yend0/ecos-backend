import abc


from ecos_backend.common.interfaces.repository import (
    AbstractRepository,
    AbstractSqlRepository,
)
from ecos_backend.models.waste import WasteDTO

from sqlalchemy.ext import asyncio


class WasteAbstractReposity(AbstractRepository[WasteDTO]):
    @abc.abstractmethod
    async def delete(self, waste: WasteDTO) -> None:
        raise NotImplementedError()


class WasteReposity(AbstractSqlRepository[WasteDTO], WasteAbstractReposity):
    def __init__(self, session: asyncio.AsyncSession) -> None:
        super().__init__(session, WasteDTO)

    async def delete(self, waste: WasteDTO) -> None:
        await self._session.delete(waste)
        await self._session.commit()
