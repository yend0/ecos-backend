import abc
import uuid

from sqlalchemy import Delete, delete, or_, select


from ecos_backend.common.interfaces.repository import (
    AbstractRepository,
    AbstractSqlRepository,
)

from ecos_backend.db.adapters import orm
from ecos_backend.models.accrual_history import AccrualHistoryDTO


class AccrualHistoryAbstractReposity(AbstractRepository, abc.ABC):
    @abc.abstractmethod
    async def get_user_accrual_histories(
        self, user_id: uuid.UUID, limit: int
    ) -> list[AccrualHistoryDTO]:
        raise NotImplementedError()


class AccrualHistoryReposity(AbstractSqlRepository, AccrualHistoryAbstractReposity):
    async def get_user_accrual_histories(
        self, user_id: uuid.UUID, limit: int
    ) -> list[AccrualHistoryDTO]:
        stmt = (
            select(
                orm.accrual_history_table,
                orm.accrual_history_table.c.reward,
                orm.accrual_history_table.c.points,
                orm.accrual_history_table.c.user_id,
            )
            .where(orm.accrual_history_table.c.user_id == user_id)
            .limit(limit)
        )

        result = await self._session.execute(stmt)
        rows = result.mappings().all()

        if not rows:
            return []

        accural_history_data_list = []
        for row in rows:
            row_dict = dict(row)
            accural_history_data_list.append(
                AccrualHistoryDTO(
                    id=row_dict["id"],
                    reward=row_dict["reward"],
                    points=row_dict["points"],
                    user_id=row_dict["user_id"],
                )
            )

        return accural_history_data_list

    async def get_by_id(self, id: uuid.UUID) -> AccrualHistoryDTO | None:
        stmt = select(
            orm.accrual_history_table,
            orm.accrual_history_table.c.id,
            orm.accrual_history_table.c.reward,
            orm.accrual_history_table.c.points,
            orm.accrual_history_table.c.user_id,
        ).where(orm.accrual_history_table.c.id == id)

        result = await self._session.execute(stmt)
        row = result.mappings().first()

        if not row:
            return None

        row_dict = dict(row)

        return AccrualHistoryDTO(
            id=row_dict["id"],
            reward=row_dict["reward"],
            points=row_dict["points"],
            user_id=row_dict["user_id"],
        )

    async def get_all(self, filters: str | None = None) -> list[AccrualHistoryDTO]:
        stmt = select(
            orm.accrual_history_table,
            orm.accrual_history_table.c.reward,
            orm.accrual_history_table.c.points,
            orm.accrual_history_table.c.user_id,
        )

        conditions = []

        if filters and filters != "null":
            try:
                criteria = dict(x.split("*") for x in filters.split("-"))
                for attr, value in criteria.items():
                    column = getattr(orm.accrual_history_table.c, attr, None)
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

        accural_history_data_list = []
        for row in rows:
            row_dict = dict(row)
            accural_history_data_list.append(
                AccrualHistoryDTO(
                    id=row_dict["id"],
                    reward=row_dict["reward"],
                    points=row_dict["points"],
                    user_id=row_dict["user_id"],
                )
            )

        return accural_history_data_list

    async def add(self, model: AccrualHistoryDTO) -> AccrualHistoryDTO:
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return model

    async def delete(self, id: uuid.UUID) -> None:
        stmt: Delete = delete(orm.accrual_history_table).where(
            orm.accrual_history_table.c.id == id
        )
        await self._session.execute(stmt)
        await self._session.commit()
