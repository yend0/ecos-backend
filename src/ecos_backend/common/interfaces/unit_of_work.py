import abc

from ecos_backend.db.repositories import (
    user,
    waste,
    waste_translation,
    work_schedule,
    accrual_history,
    reception_point,
    reception_image,
    user_image,
    user_achievement,
)


class AbstractUnitOfWork(abc.ABC):
    user: user.UserAbstractReposity
    waste: waste.WasteAbstractReposity
    waste_translation: waste_translation.WasteTranslationAbstractReposity
    work_schedule: work_schedule.WorkScheduleAbstractReposity
    user_image: user_image.UserImageAbstractReposity
    reception_point: reception_point.ReceptionPointAbstractReposity
    reception_image: reception_image.ReceptionImageAbstractReposity
    accrual_history: accrual_history.AccrualHistoryAbstractReposity
    user_achievement: user_achievement.UserAchievementAbstractReposity

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
