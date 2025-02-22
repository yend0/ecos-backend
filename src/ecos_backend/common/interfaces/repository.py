import abc
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from ecos_backend.common.interfaces.model import AbstractModel


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    async def get_by_id(self, id: uuid.UUID) -> AbstractModel | None:
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_all(self, filters: str | None) -> list[AbstractModel]:
        raise NotImplementedError()

    @abc.abstractmethod
    async def add(self, model: AbstractModel) -> AbstractModel:
        raise NotImplementedError()

    @abc.abstractmethod
    async def delete(self, id: uuid.UUID) -> None:
        raise NotImplementedError()


class AbstractSqlRepository(AbstractRepository, abc.ABC):
    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session
