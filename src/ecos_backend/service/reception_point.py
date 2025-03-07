import os
import uuid

from urllib.parse import urlparse

from ecos_backend.models.moderation import ModerationDTO
from ecos_backend.models.reception_point import ReceptionPointDTO
from ecos_backend.models.drop_off_point_waste import DropOffPointWasteDTO

from ecos_backend.common.interfaces.unit_of_work import AbstractUnitOfWork
from ecos_backend.common.config import s3_config
from ecos_backend.common import exception as custom_exceptions
from ecos_backend.common import enums
from ecos_backend.db.s3_storage import Boto3DAO


class ReceptionPointService:
    def __init__(
        self,
        uow: AbstractUnitOfWork,
        s3_storage: Boto3DAO,
    ) -> None:
        self._uow: AbstractUnitOfWork = uow
        self._s3_storage: Boto3DAO = s3_storage

    async def add_reception_point(
        self,
        reception_point: ReceptionPointDTO,
        uploaded_files: list,
    ) -> ReceptionPointDTO:
        async with self._uow:
            base_clean_url: str = ""

            for uploaded_file in uploaded_files:
                url = self._s3_storage.upload_object(
                    bucket_name=s3_config.RECEPTION_POINT_BUCKET,
                    prefix=f"{str(reception_point.id)}/images",
                    source_file_name=str(f"{uuid.uuid4()}.{uploaded_file[2]}"),
                    content=uploaded_file[1],
                )
                base_clean_url = url.rsplit("/", 1)[0] + "/"

                reception_point.set_images_url(base_clean_url)

            await self._uow.reception_point.add(reception_point)

            for i in range(0, len(reception_point.work_schedules)):
                reception_point.work_schedules[i].set_reception_point_id(
                    reception_point.id
                )
                await self._uow.work_schedule.add(reception_point.work_schedules[i])

            await self._uow.commit()

            prefixes: list[str] = self._s3_storage.get_objects(
                bucket_name=s3_config.RECEPTION_POINT_BUCKET,
                prefix=reception_point.images_url,
            )
            urls: list[str] = [
                f"{s3_config.ENDPOINT}/{s3_config.RECEPTION_POINT_BUCKET}/{prefix}"
                for prefix in prefixes
            ]
            reception_point.set_image_urls(urls)

            return reception_point

    async def get_reception_points(
        self, filters: str | None = None
    ) -> list[ReceptionPointDTO]:
        async with self._uow:
            reception_points: list[
                ReceptionPointDTO
            ] = await self._uow.reception_point.get_all(filters)
            for reception_point in reception_points:
                prefixes: list[str] = self._s3_storage.get_objects(
                    bucket_name=s3_config.RECEPTION_POINT_BUCKET,
                    prefix=reception_point.images_url,
                )
                urls: list[str] = [
                    f"{s3_config.ENDPOINT}/{s3_config.RECEPTION_POINT_BUCKET}/{prefix}"
                    for prefix in prefixes
                ]
                reception_point.set_image_urls(urls)
            return reception_points

    async def delete_reception_point(self, id: uuid.UUID) -> None:
        async with self._uow:
            reception_point: ReceptionPointDTO = await self.get_reception_point_by_id(
                id
            )
            if reception_point is not None:
                for url in reception_point.urls:
                    self._s3_storage.delete_object(
                        bucket_name=s3_config.RECEPTION_POINT_BUCKET,
                        prefix=reception_point.images_url,
                        source_file_name=os.path.basename(urlparse(url).path),
                    )
                await self._uow.reception_point.delete(reception_point.id)
                await self._uow.commit()
            else:
                raise custom_exceptions.NotFoundException(
                    detail="Reception point not found."
                )

    async def get_reception_point_by_id(
        self, id: uuid.UUID
    ) -> ReceptionPointDTO | None:
        async with self._uow:
            reception_point: (
                ReceptionPointDTO | None
            ) = await self._uow.reception_point.get_by_id(id=id)
            if not reception_point:
                return None
            prefixes: list[str] = self._s3_storage.get_objects(
                bucket_name=s3_config.RECEPTION_POINT_BUCKET,
                prefix=reception_point.images_url,
            )
            urls: list[str] = [
                f"{s3_config.ENDPOINT}/{s3_config.RECEPTION_POINT_BUCKET}/{prefix}"
                for prefix in prefixes
            ]
            reception_point.set_image_urls(urls)
            return reception_point

    async def add_drop_off_point_waste(
        self,
        drop_off_point_wast: DropOffPointWasteDTO,
    ) -> None:
        async with self._uow:
            await self._uow.reception_point.add_drop_off_point_waste(
                drop_off_point_wast
            )
            await self._uow.commit()

    async def delete_drop_off_point_waste(
        self,
        drop_off_point_wast: DropOffPointWasteDTO,
    ) -> None:
        async with self._uow:
            await self._uow.reception_point.delete_drop_off_point_waste(
                waste_id=drop_off_point_wast.waste_id,
                reception_point_id=drop_off_point_wast.reception_point_id,
            )
            await self._uow.commit()

    async def update_status_reception_point(
        self,
        reception_point: ReceptionPointDTO,
        comment: str,
        status: enums.PointStatus,
        user_id: uuid.UUID,
    ) -> ReceptionPointDTO:
        async with self._uow:
            reception_point.set_status(status=status)
            moderation = ModerationDTO(
                comment=comment,
                reception_point_id=reception_point.id,
                user_id=user_id,
            )

            await self._uow.reception_point.add(reception_point)
            await self._uow.moderation.add(moderation)

            await self._uow.commit()

            return reception_point
