import abc
from collections import defaultdict
import uuid

from sqlalchemy import and_, delete, join, select


from ecos_backend.common.interfaces.repository import (
    AbstractRepository,
    AbstractSqlRepository,
)

from ecos_backend.db.adapters import orm


from ecos_backend.models.reception_point import ReceptionPointDTO
from ecos_backend.models.work_schedule import WorkScheduleDTO


class ReceptionPointAbstractReposity(AbstractRepository, abc.ABC):
    pass


class ReceptionPointReposity(AbstractSqlRepository, AbstractRepository):
    async def get_by_id(self, id: uuid.UUID) -> ReceptionPointDTO | None:
        stmt = (
            select(
                orm.reception_point_table,
                orm.work_schedule_table,
            )
            .select_from(
                join(
                    orm.reception_point_table,
                    orm.work_schedule_table,
                    orm.reception_point_table.c.id
                    == orm.work_schedule_table.c.reception_point_id,
                )
            )
            .where(orm.reception_point_table.c.id == id)
        )

        result = await self._session.execute(stmt)
        rows = result.mappings().all()

        if not rows:
            return None

        work_schedules_map = defaultdict(list)
        reception_point_data = None
        for row in rows:
            row_dict = dict(row)

            if reception_point_data is None:
                reception_point_data = {
                    "id": row_dict["id"],
                    "name": row_dict["name"],
                    "address": row_dict["address"],
                    "user_id": row_dict["user_id"],
                    "urls": row_dict.get("urls", []) or [],
                    "status": row_dict.get("status"),
                    "images_url": row_dict.get("images_url"),
                    "updated_at": row_dict.get("updated_at"),
                    "work_schedules": [],
                }

            if row_dict["reception_point_id"]:
                work_schedules_map[row_dict["reception_point_id"]].append(
                    WorkScheduleDTO(
                        id=row_dict["id_1"],
                        day_of_week=row_dict["day_of_week"],
                        open_time=row_dict.get("open_time"),
                        close_time=row_dict.get("close_time"),
                        reception_point_id=row_dict["reception_point_id"],
                    )
                )

        if reception_point_data:
            reception_point_data["work_schedules"] = work_schedules_map.get(id, [])

        return ReceptionPointDTO(**reception_point_data)

    async def get_all(self, **filters) -> list[ReceptionPointDTO]:
        stmt = select(
            orm.reception_point_table,
            orm.work_schedule_table,
        ).select_from(
            join(
                orm.reception_point_table,
                orm.work_schedule_table,
                orm.reception_point_table.c.id
                == orm.work_schedule_table.c.reception_point_id,
            )
        )

        conditions = []
        for key, value in filters.items():
            if hasattr(orm.reception_point_table.c, key):
                conditions.append(getattr(orm.reception_point_table.c, key) == value)
        if conditions:
            stmt = stmt.where(and_(*conditions))

        result = await self._session.execute(stmt)
        rows = result.mappings().all()

        if not rows:
            return []

        reception_points_map = {}
        work_schedules_map = defaultdict(list)

        for row in rows:
            row_dict = dict(row)
            point_id = row_dict["id"]

            if point_id not in reception_points_map:
                reception_points_map[point_id] = {
                    "id": row_dict["id"],
                    "name": row_dict["name"],
                    "address": row_dict["address"],
                    "user_id": row_dict["user_id"],
                    "urls": row_dict.get("urls", []) or [],
                    "status": row_dict.get("status"),
                    "images_url": row_dict.get("images_url"),
                    "updated_at": row_dict.get("updated_at"),
                    "work_schedules": [],
                }

            if row_dict["reception_point_id"]:
                work_schedules_map[point_id].append(
                    WorkScheduleDTO(
                        id=row_dict["id_1"],
                        day_of_week=row_dict["day_of_week"],
                        open_time=row_dict.get("open_time"),
                        close_time=row_dict.get("close_time"),
                        reception_point_id=row_dict["reception_point_id"],
                    )
                )

        for point_id, reception_point_data in reception_points_map.items():
            reception_point_data["work_schedules"] = work_schedules_map.get(
                point_id, []
            )

        return [ReceptionPointDTO(**data) for data in reception_points_map.values()]

    async def add(self, model: ReceptionPointDTO) -> ReceptionPointDTO:
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return model

    async def delete(self, id: uuid.UUID) -> None:
        stmt = delete(orm.reception_point_table).where(
            orm.reception_point_table.c.id == id
        )
        await self._session.execute(stmt)
        await self._session.commit()
