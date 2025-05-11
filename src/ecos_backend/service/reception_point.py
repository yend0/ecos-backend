import uuid
import dataclasses


from sqlalchemy.orm import selectinload

from ecos_backend.common.interfaces.unit_of_work import AbstractUnitOfWork
from ecos_backend.common.config import s3_config
from ecos_backend.common import exception as exc
from ecos_backend.common import enums

from ecos_backend.db.models.accrual_history import AccrualHistory
from ecos_backend.db.models.reception_image import ReceptionImage
from ecos_backend.db.models.reception_point import ReceptionPoint
from ecos_backend.db.models.work_schedule import WorkSchedule

from ecos_backend.db.s3_storage import Boto3DAO


@dataclasses.dataclass(kw_only=True, frozen=True, slots=True)
class ReceptionPointService:
    uow: AbstractUnitOfWork
    s3_storage: Boto3DAO

    async def add_reception_point(
        self,
        user_id: uuid.UUID,
        reception_point: ReceptionPoint,
        work_schedule: list,
        waste_ids: list[uuid.UUID],
        uploaded_files: list[tuple[str, bytes, str]],  # (filename, content, extension)
    ) -> ReceptionPoint:
        """Add new reception point with uploaded images."""
        async with self.uow:
            try:
                filenames: list[str] = []

                for _, _, ext in uploaded_files:
                    filenames.append(f"{uuid.uuid4()}.{ext}")

                # 1. Save reception point to get ID
                await self.uow.reception_point.add(reception_point)

                # 2. Process uploaded files
                await self._upload_images(reception_point.id, uploaded_files, filenames)

                # 3. Save work schedules
                for schedule in work_schedule:
                    schedule_data = schedule.dict(exclude_unset=True)
                    work_schedule = WorkSchedule(
                        id=uuid.uuid4(),
                        day_of_week=schedule_data.get("day_of_week"),
                        open_time=schedule_data.get("open_time"),
                        close_time=schedule_data.get("close_time"),
                        reception_point_id=reception_point.id,
                    )
                    await self.uow.work_schedule.add(work_schedule)

                # 4. Save reception images
                for filename in filenames:
                    reception_image = ReceptionImage(
                        id=uuid.uuid4(),
                        reception_point_id=reception_point.id,
                        filename=filename,
                    )
                    await self.uow.reception_image.add(reception_image)

                # 5. Save waste types
                for waste_id in waste_ids:
                    await self.uow.reception_point.add_waste_type(
                        reception_point_id=reception_point.id, waste_id=waste_id
                    )

                await self.uow.reception_point.add_user(
                    reception_point_id=reception_point.id, user_id=user_id
                )

                await self.uow.commit()
                return reception_point

            except Exception as e:
                await self.uow.rollback()
                # Cleanup uploaded images if any error occurs
                if reception_point.id:
                    await self._delete_images(reception_point.id, filenames)
                raise exc.InternalServerException(
                    detail=f"Failed to add reception point: {str(e)}"
                )

    async def add_waste_in_reception_point(
        self,
        reception_point_id: uuid.UUID,
        waste_id: uuid.UUID,
    ) -> None:
        """Add waste type to reception point."""
        async with self.uow:
            try:
                await self.uow.reception_point.add_waste_type(
                    reception_point_id=reception_point_id, waste_id=waste_id
                )
                await self.uow.commit()
            except Exception as e:
                await self.uow.rollback()
                raise exc.InternalServerException(
                    detail=f"Failed to add waste type: {str(e)}"
                )

    async def delete_waste_from_reception_point(
        self,
        reception_point_id: uuid.UUID,
        waste_id: uuid.UUID,
    ) -> None:
        """Delete waste type from reception point."""
        async with self.uow:
            try:
                await self.uow.reception_point.delete_waste_type(
                    reception_point_id=reception_point_id, waste_id=waste_id
                )
                await self.uow.commit()
            except Exception as e:
                await self.uow.rollback()
                raise exc.InternalServerException(
                    detail=f"Failed to delete waste type: {str(e)}"
                )

    async def get_reception_points(
        self,
        filters: dict | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        page: int = 1,
        per_page: int = 10,
    ) -> list[ReceptionPoint]:
        """Get list of reception points with their images."""
        async with self.uow:
            try:
                options: list = []
                options.append(selectinload(ReceptionPoint.work_schedules))
                options.append(selectinload(ReceptionPoint.reception_images))
                options.append(selectinload(ReceptionPoint.wastes))

                radius = filters.pop("radius", None)

                if (
                    radius is not None
                    and latitude is not None
                    and longitude is not None
                ):
                    points = await self.uow.reception_point.get_nearby_points(
                        user_lat=latitude,
                        user_lon=longitude,
                        radius_meters=radius,
                        filters=filters,
                        page=page,
                        per_page=per_page,
                        options=options,
                    )
                else:
                    points: list[
                        ReceptionPoint
                    ] = await self.uow.reception_point.get_all(
                        filters=filters,
                        options=options,
                        limit=per_page,
                        offset=(page - 1) * per_page,
                    )
                return points
            except Exception as e:
                raise exc.InternalServerException(
                    detail=f"Failed to get reception points: {str(e)}"
                )

    async def get_reception_point_by_id(self, id: uuid.UUID) -> ReceptionPoint | None:
        """Get single reception point by ID with images."""
        async with self.uow:
            try:
                options: list = []
                options.append(selectinload(ReceptionPoint.work_schedules))
                options.append(selectinload(ReceptionPoint.reception_images))
                options.append(selectinload(ReceptionPoint.wastes))
                options.append(selectinload(ReceptionPoint.users))

                point: ReceptionPoint | None = await self.uow.reception_point.get_by_id(
                    id=id, options=options
                )

                return point
            except Exception as e:
                raise exc.InternalServerException(
                    detail=f"Failed to get reception point: {str(e)}"
                )

    async def delete_reception_point(self, id: uuid.UUID) -> None:
        """Delete reception point and all associated data."""
        async with self.uow:
            try:
                point: ReceptionPoint | None = await self.get_reception_point_by_id(id)
                if not point:
                    raise exc.NotFoundException(detail="Reception point not found")

                # Delete associated images
                if len(point.reception_images) > 0:
                    await self._delete_images(
                        point.id, [img.filename for img in point.reception_images]
                    )

                # Delete main record
                await self.uow.reception_point.delete(point)
                await self.uow.commit()

            except exc.NotFoundException:
                raise
            except Exception as e:
                await self.uow.rollback()
                raise exc.InternalServerException(
                    detail=f"Failed to delete reception point: {str(e)}"
                )

    async def update_status(
        self,
        reception_point: ReceptionPoint,
        status: enums.PointStatus,
        user_id: uuid.UUID,
    ) -> ReceptionPoint:
        """Update reception point status"""
        async with self.uow:
            try:
                reception_point.status = status

                # # Create accrual history
                points = 0 if status == enums.PointStatus.REJECTED else 10

                accrual = AccrualHistory(
                    points=points,
                    user_id=user_id,
                    reward=enums.RewardType.RECYCLE_POINT_ADD,
                )

                await self.uow.accrual_history.add(accrual)
                await self.uow.reception_point.add(reception_point)
                await self.uow.commit()

                return reception_point

            except exc.NotFoundException:
                raise
            except Exception as e:
                await self.uow.rollback()
                raise exc.InternalServerException(
                    detail=f"Failed to update status: {str(e)}"
                )

    # Private helper methods
    async def _upload_images(
        self,
        point_id: uuid.UUID,
        files: list[tuple[str, bytes, str]],
        filenames: list[str],
    ) -> list[str]:
        """Upload images to S3 and return URLs."""
        urls = []
        i = 0
        for _, content, _ in files:
            try:
                url = self.s3_storage.upload_object(
                    bucket_name=s3_config.RECEPTION_POINT_BUCKET,
                    prefix=f"{point_id}/images",
                    source_file_name=filenames[i],
                    content=content,
                )
                urls.append(url.split("?")[0])
                i += 1
            except Exception as e:
                # Cleanup already uploaded files if one fails
                self._delete_images(point_id)
                raise exc.InternalServerException(
                    detail=f"Failed to upload image: {str(e)}"
                )
        return urls

    async def _delete_images(
        self,
        point_id: uuid.UUID,
        filenames: list[str],
    ) -> None:
        """Delete images from S3."""
        try:
            for filename in filenames:
                self.s3_storage.delete_object(
                    bucket_name=s3_config.RECEPTION_POINT_BUCKET,
                    prefix=f"{point_id}/images",
                    source_file_name=filename,
                )
        except Exception as e:
            raise exc.InternalServerException(
                detail=f"Failed to delete images: {str(e)}"
            )
