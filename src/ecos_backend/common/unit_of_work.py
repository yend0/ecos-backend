from sqlalchemy.ext.asyncio import AsyncSession

from ecos_backend.common.interfaces.unit_of_work import AbstractUnitOfWork

from ecos_backend.db.repositories.user import UserReposity
from ecos_backend.db.repositories.reception_point import ReceptionPointReposity
from ecos_backend.db.repositories.waste import WasteReposity
from ecos_backend.db.repositories.work_schedule import WorkScheduleReposity
from ecos_backend.db.repositories.moderation import ModerationReposity
from ecos_backend.db.repositories.accrual_history import AccrualHistoryReposity
from ecos_backend.db.repositories.user_image import UserImageReposity
from ecos_backend.db.repositories.reception_image import ReceptionImageReposity


from ecos_backend.db.models.user import User
from ecos_backend.db.models.reception_point import ReceptionPoint
from ecos_backend.db.models.waste import Waste
from ecos_backend.db.models.waste_translation import WasteTranslation
from ecos_backend.db.models.work_schedule import WorkSchedule
from ecos_backend.db.models.moderation import Moderation
from ecos_backend.db.models.accrual_history import AccrualHistory
from ecos_backend.db.models.user_image import UserImage
from ecos_backend.db.models.reception_image import ReceptionImage


class SQLAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def __aenter__(self) -> "SQLAlchemyUnitOfWork":
        self.user = UserReposity(self._session, User)
        self.user_image = UserImageReposity(self._session, UserImage)
        self.reception_point = ReceptionPointReposity(self._session, ReceptionPoint)
        self.reception_image = ReceptionImageReposity(self._session, ReceptionImage)
        self.waste = WasteReposity(self._session, Waste)
        self.waste_translation = WasteReposity(self._session, WasteTranslation)
        self.work_schedule = WorkScheduleReposity(self._session, WorkSchedule)
        self.moderation = ModerationReposity(self._session, Moderation)
        self.accrual_history = AccrualHistoryReposity(self._session, AccrualHistory)

        return await super().__aenter__()

    async def __aexit__(self, *args, **kwargs) -> None:
        await super().__aexit__(*args, **kwargs)
        await self._session.close()

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        """
        Rollbacks all uncommited changes.

        Uses self._session.expunge_all() to avoid sqlalchemy.orm.exc.DetachedInstanceError after session rollback,
        due to the fact that selected object is cached by Session. And self._session.rollback() deletes all Session
        cache, which causes error on Domain model, which is not bound now to the session and can not retrieve
        attributes.

        https://pythonhint.com/post/1123713161982291/how-does-a-sqlalchemy-object-get-detached
        """

        self._session.expunge_all()
        await self._session.rollback()
