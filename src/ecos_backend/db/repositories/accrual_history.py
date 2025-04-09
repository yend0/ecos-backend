import abc

from ecos_backend.common.interfaces.repository import (
    AbstractRepository,
    AbstractSqlRepository,
)

from ecos_backend.db.models.accrual_history import AccrualHistory


class AccrualHistoryAbstractReposity(AbstractRepository[AccrualHistory], abc.ABC):
    # @abc.abstractmethod
    # async def get_user_accrual_histories(
    #     self, user_id: uuid.UUID, limit: int
    # ) -> list[AccrualHistory]:
    #     raise NotImplementedError()
    pass


class AccrualHistoryReposity(
    AbstractSqlRepository[AccrualHistory], AccrualHistoryAbstractReposity
):
    pass
