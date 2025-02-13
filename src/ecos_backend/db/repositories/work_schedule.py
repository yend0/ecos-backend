from ecos_backend.common.interfaces.repository import (
    AbstractRepository,
    AbstractSqlRepository,
)
from ecos_backend.domain.work_schedule import WorkScheduleModel

from sqlalchemy.ext import asyncio


class WorkScheduleAbstractReposity(AbstractRepository[WorkScheduleModel]):
    pass


class WorkScheduleReposity(
    AbstractSqlRepository[WorkScheduleModel], WorkScheduleAbstractReposity
):
    def __init__(self, session: asyncio.AsyncSession) -> None:
        super().__init__(session, WorkScheduleModel)
