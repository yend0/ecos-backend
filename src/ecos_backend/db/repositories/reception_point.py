import abc
from collections import defaultdict
import uuid

from sqlalchemy import delete, join, or_, select


from ecos_backend.common.interfaces.model import AbstractModel
from ecos_backend.common.interfaces.repository import (
    AbstractRepository,
    AbstractSqlRepository,
)

from ecos_backend.db.adapters import orm


from ecos_backend.models.drop_off_point_waste import DropOffPointWasteDTO
from ecos_backend.models.reception_point import ReceptionPointDTO
from ecos_backend.models.work_schedule import WorkScheduleDTO


class ReceptionPointAbstractReposity(AbstractRepository, abc.ABC):
    @abc.abstractmethod
    async def add_drop_off_point_waste(self, model: AbstractModel) -> AbstractModel:
        raise NotImplementedError()

    @abc.abstractmethod
    async def delete_drop_off_point_waste(
        self,
        reception_point_id: uuid.UUID,
        waste_id: uuid.UUID,
    ) -> None:
        raise NotImplementedError()


class ReceptionPointReposity(AbstractSqlRepository, AbstractRepository):
    async def get_by_id(self, id: uuid.UUID) -> ReceptionPointDTO | None:
        stmt = (
            select(
                orm.reception_point_table,
                orm.work_schedule_table,
                orm.drop_off_point_waste_table.c.waste_id,
            )
            .select_from(
                join(
                    join(
                        orm.reception_point_table,
                        orm.drop_off_point_waste_table,
                        orm.reception_point_table.c.id
                        == orm.drop_off_point_waste_table.c.reception_point_id,
                        isouter=True,
                    ),
                    orm.work_schedule_table,
                    orm.reception_point_table.c.id
                    == orm.work_schedule_table.c.reception_point_id,
                    isouter=True,
                )
            )
            .where(orm.reception_point_table.c.id == id)
        )

        result = await self._session.execute(stmt)
        rows = result.mappings().all()

        if not rows:
            return None

        work_schedules_map = defaultdict(list)
        waste_ids = set()
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
                    "description": row_dict["description"],
                    "images_url": row_dict.get("images_url"),
                    "updated_at": row_dict.get("updated_at"),
                    "work_schedules": [],
                    "waste_ids": [],
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

            if row_dict.get("waste_id"):
                waste_ids.add(row_dict["waste_id"])

        if reception_point_data:
            reception_point_data["work_schedules"] = work_schedules_map.get(id, [])
            reception_point_data["waste_ids"] = list(waste_ids)

        return ReceptionPointDTO(**reception_point_data)

    async def get_all(self, filters: str | None = None) -> list[ReceptionPointDTO]:
        stmt = select(
            orm.reception_point_table,
            orm.work_schedule_table,
            orm.drop_off_point_waste_table.c.waste_id,
        ).select_from(
            orm.reception_point_table.outerjoin(
                orm.drop_off_point_waste_table,
                orm.reception_point_table.c.id
                == orm.drop_off_point_waste_table.c.reception_point_id,
            ).outerjoin(
                orm.work_schedule_table,
                orm.reception_point_table.c.id
                == orm.work_schedule_table.c.reception_point_id,
            )
        )

        conditions = []

        if filters and filters != "null":
            try:
                criteria = dict(x.split("*") for x in filters.split("-"))
                for attr, value in criteria.items():
                    column = getattr(orm.reception_point_table.c, attr, None)
                    if column is not None:
                        if column.type.python_type is str:
                            conditions.append(column.ilike(f"%{value}%"))
                        else:
                            conditions.append(column == value)
            except Exception as e:
                print(f"Ошибка обработки фильтра: {e}")

        if conditions:
            stmt = stmt.where(or_(*conditions))

        result = await self._session.execute(stmt)
        rows = result.mappings().all()

        if not rows:
            return []

        reception_points_map = {}
        work_schedules_map = defaultdict(list)
        wastes_map = defaultdict(set)

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
                    "description": row_dict["description"],
                    "images_url": row_dict.get("images_url"),
                    "updated_at": row_dict.get("updated_at"),
                    "work_schedules": [],
                    "waste_ids": set(),
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

            if row_dict["waste_id"]:
                wastes_map[point_id].add(row_dict["waste_id"])

        for point_id, reception_point_data in reception_points_map.items():
            reception_point_data["work_schedules"] = work_schedules_map.get(
                point_id, []
            )
            reception_point_data["waste_ids"] = list(wastes_map.get(point_id, []))

        return [ReceptionPointDTO(**data) for data in reception_points_map.values()]

    async def add(self, model: ReceptionPointDTO) -> ReceptionPointDTO:
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return model

    async def add_drop_off_point_waste(
        self, model: DropOffPointWasteDTO
    ) -> DropOffPointWasteDTO:
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

    async def delete_drop_off_point_waste(
        self,
        reception_point_id: uuid.UUID,
        waste_id: uuid.UUID,
    ) -> None:
        stmt = delete(orm.drop_off_point_waste_table).where(
            orm.drop_off_point_waste_table.c.waste_id == waste_id,
            orm.drop_off_point_waste_table.c.reception_point_id == reception_point_id,
        )
        await self._session.execute(stmt)
        await self._session.commit()
