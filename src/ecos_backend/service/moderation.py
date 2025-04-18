import dataclasses

from sqlalchemy.orm import selectinload

from ecos_backend.db.models.moderation import Moderation

from ecos_backend.common.interfaces.unit_of_work import AbstractUnitOfWork


@dataclasses.dataclass(kw_only=True, frozen=True, slots=True)
class ModerationService:
    uow: AbstractUnitOfWork

    async def get_moderations(self, filters: str | None = None) -> list[Moderation]:
        async with self.uow:
            options: list = []
            options.append(selectinload(Moderation.user))
            options.append(selectinload(Moderation.reception_point))

            moderations: list[Moderation] = await self.uow.moderation.get_all(
                filters=filters,
                options=options,
            )
            return moderations
