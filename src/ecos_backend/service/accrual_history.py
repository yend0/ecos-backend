import uuid


from ecos_backend.models.accrual_history import AccrualHistoryDTO

from ecos_backend.common.interfaces.unit_of_work import AbstractUnitOfWork


class AccrualHistoryService:
    def __init__(
        self,
        uow: AbstractUnitOfWork,
    ) -> None:
        self._uow: AbstractUnitOfWork = uow

    async def get_user_accrual_histories(
        self, user_id: uuid.UUID, limit: int = 100
    ) -> list[AccrualHistoryDTO]:
        async with self._uow:
            accrual_histories: list[
                AccrualHistoryDTO
            ] = await self._uow.accrual_history.get_user_accrual_histories(
                user_id=user_id,
                limit=limit,
            )
            return accrual_histories

    async def get_accrual_histories(
        self, filters: str | None = None
    ) -> list[AccrualHistoryDTO]:
        async with self._uow:
            accrual_histories: list[
                AccrualHistoryDTO
            ] = await self._uow.accrual_history.get_all(filters=filters)
            return accrual_histories

    async def get_accrual_history_by_id(
        self, id: uuid.UUID
    ) -> AccrualHistoryDTO | None:
        async with self._uow:
            accrual_history: (
                AccrualHistoryDTO | None
            ) = await self._uow.accrual_history.get_by_id(id=id)
            return accrual_history
