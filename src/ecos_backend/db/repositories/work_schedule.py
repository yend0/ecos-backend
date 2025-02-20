import abc
import uuid

from sqlalchemy import Result, Select, and_, delete, select

from ecos_backend.common.interfaces.repository import (
    AbstractRepository,
    AbstractSqlRepository,
)

from ecos_backend.db.adapters import orm
from ecos_backend.models.work_schedule import WorkScheduleDTO


class WorkScheduleAbstractReposity(AbstractRepository, abc.ABC):
    pass


class WorkScheduleReposity(AbstractSqlRepository, WorkScheduleAbstractReposity):
    async def get_by_id(self, id: uuid.UUID) -> WorkScheduleDTO | None:
        stmt: Select = self._construct_get_stmt(id)
        result: Result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, **filters) -> list[WorkScheduleDTO]:
        stmt: Select = self._construct_get_all_stmt(**filters)
        result: Result = await self._session.execute(stmt)
        return result.scalars().all()

    async def add(self, model: WorkScheduleDTO) -> WorkScheduleDTO:
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return model

    async def delete(self, id: uuid.UUID) -> None:
        stmt = delete(orm.work_schedule_table).where(orm.work_schedule_table.c.id == id)
        await self._session.execute(stmt)
        await self._session.commit()

    def _construct_get_stmt(self, id: int) -> Select:
        stmt: Select = select(WorkScheduleDTO).where(orm.work_schedule_table.c.id == id)
        return stmt

    def _construct_get_all_stmt(self, **filters) -> Select:
        stmt: Select = select(WorkScheduleDTO)
        where_clauses: list = []

        for c, v in filters.items():
            if not hasattr(orm.work_schedule_table.c, c):
                raise ValueError(f"Invalid column name {c}")
            where_clauses.append(getattr(orm.work_schedule_table.c, c) == v)

        if len(where_clauses) == 1:
            stmt = stmt.where(where_clauses[0])
        elif len(where_clauses) > 1:
            stmt = stmt.where(and_(*where_clauses))
        return stmt
