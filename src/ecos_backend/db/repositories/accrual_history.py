import abc

from ecos_backend.db.models.accrual_history import AccrualHistory

from ecos_backend.common.interfaces.repository import (
    AbstractRepository,
    AbstractSqlRepository,
)


class AccrualHistoryAbstractReposity(AbstractRepository[AccrualHistory], abc.ABC):
    pass


class AccrualHistoryReposity(
    AbstractSqlRepository[AccrualHistory], AccrualHistoryAbstractReposity
):
    pass
