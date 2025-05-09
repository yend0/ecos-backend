import os
import uuid
import dataclasses

from urllib.parse import urlparse

from sqlalchemy.orm import selectinload

from ecos_backend.db.models.waste import Waste
from ecos_backend.db.models.waste_translation import WasteTranslation
from ecos_backend.common.interfaces.unit_of_work import AbstractUnitOfWork
from ecos_backend.common.config import s3_config
from ecos_backend.common import exception as custom_exceptions
from ecos_backend.db.s3_storage import Boto3DAO


@dataclasses.dataclass(kw_only=True, frozen=True, slots=True)
class WasteService:
    uow: AbstractUnitOfWork
    s3_storage: Boto3DAO

    async def add_waste(
        self,
        waste: Waste,
        waste_translations: list[WasteTranslation],
        file: bytes | None = None,
        file_extension: str | None = None,
    ) -> Waste:
        """Add new waste record with optional image."""
        async with self.uow:
            try:
                if file and file_extension:
                    filename: str = f"{uuid.uuid4()}.{file_extension}"
                    waste.id = uuid.uuid4()
                    url = self.s3_storage.upload_object(
                        bucket_name=s3_config.WASTE_BUCKET,
                        prefix=f"{waste.id}/image",
                        source_file_name=filename,
                        content=file,
                    )
                    clean_url = url.split("?")[0]
                    waste.image_url = clean_url

                await self.uow.waste.add(waste)

                for translation in waste_translations:
                    waste_translation_data = translation.dict(exclude_unset=True)
                    waste_translation = WasteTranslation(
                        id=uuid.uuid4(),
                        language_code=waste_translation_data.get("language_code"),
                        name=waste_translation_data.get("name"),
                        description=waste_translation_data.get("description"),
                        waste_id=waste.id,
                    )
                    await self.uow.work_schedule.add(waste_translation)

                await self.uow.commit()
                return waste
            except Exception as e:
                await self.uow.rollback()
                raise custom_exceptions.InternalServerException(
                    detail=f"Failed to add waste: {str(e)}"
                ) from e

    async def get_wastes(
        self, language_code: str, filters: dict | None = None
    ) -> list[Waste]:
        """Get list of wastes with their image URLs."""
        async with self.uow:
            try:
                options = [selectinload(Waste.waste_translations)]

                wastes: list[Waste] = await self.uow.waste.get_all(options=options)

                if language_code:
                    for waste in wastes:
                        waste.waste_translations = [
                            translation
                            for translation in waste.waste_translations
                            if translation.language_code.value == language_code
                        ]
                return wastes
            except Exception as e:
                raise custom_exceptions.InternalServerException(
                    detail=f"Failed to get wastes: {str(e)}"
                ) from e

    async def get_waste_by_id(self, id: uuid.UUID) -> Waste | None:
        """Get single waste by ID with image URL."""
        async with self.uow:
            try:
                waste: Waste | None = await self.uow.waste.get_by_id(id=id)
                return waste
            except Exception as e:
                raise custom_exceptions.InternalServerException(
                    detail=f"Failed to get waste: {str(e)}"
                ) from e

    async def delete_waste(self, id: uuid.UUID) -> None:
        """Delete waste record and associated image."""
        async with self.uow:
            try:
                waste: Waste | None = await self.get_waste_by_id(id)
                if not waste:
                    raise custom_exceptions.NotFoundException(detail="Waste not found")

                if waste.image_url:
                    self._delete_waste_image(waste)

                await self.uow.waste.delete(waste)
                await self.uow.commit()
            except custom_exceptions.NotFoundException:
                raise
            except Exception as e:
                await self.uow.rollback()
                raise custom_exceptions.InternalServerException(
                    detail=f"Failed to delete waste: {str(e)}"
                ) from e

    def _delete_waste_image(self, waste: Waste) -> None:
        """Delete waste image from storage."""
        try:
            waste_id_str = str(waste.id)

            self.s3_storage.delete_object(
                bucket_name=s3_config.WASTE_BUCKET,
                prefix=f"{waste_id_str}/image",
                source_file_name=os.path.basename(urlparse(waste.image_url).path),
            )
        except Exception as e:
            raise custom_exceptions.InternalServerException(
                detail=f"Failed to delete waste image: {str(e)}"
            ) from e
