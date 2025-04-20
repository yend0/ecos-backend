import abc

from ecos_backend.common.interfaces.repository import (
    AbstractRepository,
    AbstractSqlRepository,
)

from ecos_backend.db.models.work_schedule import WorkSchedule


class WorkScheduleAbstractReposity(AbstractRepository[WorkSchedule], abc.ABC):
    pass


class WorkScheduleReposity(
    AbstractSqlRepository[WorkSchedule], WorkScheduleAbstractReposity
):
    pass
