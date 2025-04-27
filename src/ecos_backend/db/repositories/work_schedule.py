import abc

from ecos_backend.db.models.work_schedule import WorkSchedule

from ecos_backend.common.interfaces.repository import (
    AbstractRepository,
    AbstractSqlRepository,
)


class WorkScheduleAbstractReposity(AbstractRepository[WorkSchedule], abc.ABC):
    pass


class WorkScheduleReposity(
    AbstractSqlRepository[WorkSchedule], WorkScheduleAbstractReposity
):
    pass
