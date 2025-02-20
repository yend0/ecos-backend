import os
import uuid

from urllib.parse import urlparse

from ecos_backend.models.waste import WasteDTO
from ecos_backend.common.interfaces.unit_of_work import AbstractUnitOfWork
from ecos_backend.common.config import s3_config
from ecos_backend.common import exception as custom_exceptions
from ecos_backend.db.s3_storage import Boto3DAO


class WasteService:
    def __init__(
        self,
        uow: AbstractUnitOfWork,
        s3_storage: Boto3DAO,
    ) -> None:
        self._uow: AbstractUnitOfWork = uow
        self._s3_storage: Boto3DAO = s3_storage

    async def add_waste(
        self,
        waste: WasteDTO,
        file: bytes = None,
        file_extention: str = None,
    ) -> WasteDTO:
        async with self._uow:
            if file_extention is not None:
                try:
                    url = self._s3_storage.upload_object(
                        bucket_name=s3_config.WASTE_BUCKET,
                        prefix=f"{str(waste.id)}/image",
                        source_file_name=str(f"{uuid.uuid4()}.{file_extention}"),
                        content=file,
                    )
                    clean_url = url.split("?")[0]
                    waste.update_image_url(clean_url)
                except Exception as e:
                    raise e

            waste = await self._uow.waste.add(waste)
            await self._uow.commit()
            return waste

    async def get_wastes(self) -> list[WasteDTO]:
        async with self._uow:
            wastes: list[WasteDTO] = await self._uow.waste.get_all()
            for waste in wastes:
                prefixes: list[str] = self._s3_storage.get_objects(
                    bucket_name=s3_config.WASTE_BUCKET,
                    prefix=f"{str(waste.id)}/image",
                )
                waste.update_image_url(
                    f"{s3_config.ENDPOINT}/{s3_config.WASTE_BUCKET}/{prefixes[0]}"
                )
            return wastes

    async def delete_waste(self, id: uuid.UUID) -> None:
        async with self._uow:
            waste: WasteDTO = await self.get_waste_by_id(id)
            if waste is not None:
                self._s3_storage.delete_object(
                    bucket_name=s3_config.WASTE_BUCKET,
                    prefix=f"{str(waste.id)}/image",
                    source_file_name=os.path.basename(urlparse(waste.image_url).path),
                )
                await self._uow.waste.delete(waste.id)
                await self._uow.commit()
            else:
                raise custom_exceptions.NotFoundException(detail="Waste not found.")

    async def get_waste_by_id(self, id: uuid.UUID) -> WasteDTO | None:
        async with self._uow:
            waste: WasteDTO | None = await self._uow.waste.get_by_id(id=id)
            if not waste:
                return None
            prefixes: list[str] = self._s3_storage.get_objects(
                bucket_name=s3_config.WASTE_BUCKET,
                prefix=f"{str(waste.id)}/image",
            )
            waste.update_image_url(
                f"{s3_config.ENDPOINT}/{s3_config.WASTE_BUCKET}/{prefixes[0]}"
            )
            return waste
