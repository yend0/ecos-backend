import abc
import uuid

from sqlalchemy import Result, Select, and_, delete, insert, select


from ecos_backend.common.interfaces.repository import (
    AbstractRepository,
    AbstractSqlRepository,
)

from ecos_backend.db.adapters import orm
from ecos_backend.models.waste import WasteDTO


class WasteAbstractReposity(AbstractRepository, abc.ABC):
    @abc.abstractmethod
    async def add_drop_off_point_waste(
        self, waste_id: uuid.UUID, reception_point_id: uuid.UUID
    ) -> None:
        raise NotImplementedError()


class WasteReposity(AbstractSqlRepository, WasteAbstractReposity):
    async def get_by_id(self, id: uuid.UUID) -> WasteDTO | None:
        stmt: Select = self._construct_get_stmt(id)
        result: Result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, filters: str | None = None) -> list[WasteDTO]:
        stmt: Select = self._construct_get_all_stmt(filters)
        result: Result = await self._session.execute(stmt)
        return result.scalars().all()

    async def add(self, model: WasteDTO) -> WasteDTO:
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return model

    async def delete(self, id: uuid.UUID) -> None:
        stmt = delete(orm.waste_table).where(orm.waste_table.c.id == id)
        await self._session.execute(stmt)
        await self._session.commit()

    def _construct_get_stmt(self, id: int) -> Select:
        stmt: Select = select(WasteDTO).where(orm.waste_table.c.id == id)
        return stmt

    def _construct_get_all_stmt(self, filters: str | None = None) -> Select:
        stmt: Select = select(WasteDTO)
        where_clauses: list = []

        if filters:
            try:
                criteria = dict(x.split("*") for x in filters.split("-"))
            except ValueError:
                raise ValueError(
                    "Invalid filter format. Expected 'key1*value1-key2*value2'"
                )

            for column_name, value in criteria.items():
                if not hasattr(orm.waste_table.c, column_name):
                    raise ValueError(f"Invalid column name {column_name}")

                where_clauses.append(
                    getattr(orm.waste_table.c, column_name).like(f"%{value}%")
                )

        if where_clauses:
            stmt = stmt.where(and_(*where_clauses))

        return stmt

    async def add_drop_off_point_waste(
        self, waste_id: uuid.UUID, reception_point_id: uuid.UUID
    ) -> None:
        stmt = insert(orm.drop_off_point_waste_table).values(
            waste_id=waste_id, reception_point_id=reception_point_id
        )
        await self._session.execute(stmt)
        await self._session.commit()
