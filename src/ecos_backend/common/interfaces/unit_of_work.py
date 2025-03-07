import abc

from ecos_backend.db.repositories import (
    user,
    reception_point,
    waste,
    work_schedule,
    moderation,
)


class AbstractUnitOfWork(abc.ABC):
    user: user.UserAbstractReposity
    reception_point: reception_point.ReceptionPointAbstractReposity
    waste: waste.WasteAbstractReposity
    work_schedule: work_schedule.WorkScheduleAbstractReposity
    moderation: moderation.ModerationAbstractReposity

    @abc.abstractmethod
    async def __aenter__(self) -> "AbstractUnitOfWork":
        return self

    @abc.abstractmethod
    async def __aexit__(self, *args, **kwargs) -> None:
        await self.rollback()

    @abc.abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError()
