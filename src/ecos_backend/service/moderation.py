import uuid


from ecos_backend.models.moderation import ModerationDTO
from ecos_backend.models.reception_point import ReceptionPointDTO

from ecos_backend.common.interfaces.unit_of_work import AbstractUnitOfWork


class ModerationService:
    def __init__(
        self,
        uow: AbstractUnitOfWork,
    ) -> None:
        self._uow: AbstractUnitOfWork = uow

    async def get_moderations(self, filters: str | None = None) -> list[ModerationDTO]:
        async with self._uow:
            moderations: list[ModerationDTO] = await self._uow.moderation.get_all(
                filters=filters
            )
            return moderations

    async def get_moderation_by_id(self, id: uuid.UUID) -> ReceptionPointDTO | None:
        async with self._uow:
            moderation: ModerationDTO | None = await self._uow.moderation.get_by_id(
                id=id
            )
            return moderation
