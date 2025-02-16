from sqlalchemy.ext import asyncio

from ecos_backend.common.interfaces.repository import (
    AbstractRepository,
    AbstractSqlRepository,
)
from ecos_backend.models.work_schedule import WorkScheduleDTO


class WorkScheduleAbstractReposity(AbstractRepository[WorkScheduleDTO]):
    pass


class WorkScheduleReposity(
    AbstractSqlRepository[WorkScheduleDTO], WorkScheduleAbstractReposity
):
    def __init__(self, session: asyncio.AsyncSession) -> None:
        super().__init__(session, WorkScheduleDTO)
