import uuid
import dataclasses

from ecos_backend.common.interfaces.unit_of_work import AbstractUnitOfWork
from ecos_backend.common import exception as custom_exceptions
from ecos_backend.db.models.waste_translation import WasteTranslation
from ecos_backend.db.s3_storage import Boto3DAO


@dataclasses.dataclass(kw_only=True, frozen=True, slots=True)
class WasteTranslationService:
    uow: AbstractUnitOfWork
    s3_storage: Boto3DAO

    async def add_waste_translation(
        self,
        waste_translation: WasteTranslation,
    ) -> WasteTranslation:
        """Add new waste translation record."""
        async with self.uow:
            try:
                await self.uow.waste_translation.add(waste_translation)
                await self.uow.commit()
                return waste_translation
            except Exception as e:
                await self.uow.rollback()
                raise custom_exceptions.InternalServerException(
                    detail=f"Failed to add waste translation: {str(e)}"
                ) from e

    async def get_waste_translations(
        self, filters: dict | None = None
    ) -> list[WasteTranslation]:
        """Get list of waste translations."""
        async with self.uow:
            try:
                waste_trnaslations: list[
                    WasteTranslation
                ] = await self.uow.waste_translation.get_all(filters=filters)
                return waste_trnaslations
            except Exception as e:
                raise custom_exceptions.InternalServerException(
                    detail=f"Failed to get waste translations: {str(e)}"
                ) from e

    async def get_waste_translation_by_id(
        self, id: uuid.UUID
    ) -> WasteTranslation | None:
        """Get single waste tranlation by ID."""
        async with self.uow:
            try:
                waste_translation: (
                    WasteTranslation | None
                ) = await self.uow.waste_translation.get_by_id(id=id)
                return waste_translation
            except Exception as e:
                raise custom_exceptions.InternalServerException(
                    detail=f"Failed to get waste translation: {str(e)}"
                ) from e

    async def delete_waste_translation(self, id: uuid.UUID) -> None:
        """Delete waste translation record."""
        async with self.uow:
            try:
                waste_translation: (
                    WasteTranslation | None
                ) = await self.get_waste_translation_by_id(id)
                if not waste_translation:
                    raise custom_exceptions.NotFoundException(
                        detail="Waste translation not found"
                    )

                await self.uow.waste_translation.delete(waste_translation)
                await self.uow.commit()
            except custom_exceptions.NotFoundException:
                raise
            except Exception as e:
                await self.uow.rollback()
                raise custom_exceptions.InternalServerException(
                    detail=f"Failed to delete waste translation: {str(e)}"
                ) from e
