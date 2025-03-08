import abc
import uuid

from sqlalchemy import delete, or_, select


from ecos_backend.common.interfaces.repository import (
    AbstractRepository,
    AbstractSqlRepository,
)

from ecos_backend.db.adapters import orm


from ecos_backend.models.moderation import ModerationDTO


class ModerationAbstractReposity(AbstractRepository, abc.ABC):
    pass


class ModerationReposity(AbstractSqlRepository, ModerationAbstractReposity):
    async def get_by_id(self, id: uuid.UUID) -> ModerationDTO | None:
        stmt = select(
            orm.moderation_table,
            orm.moderation_table.c.comment,
            orm.moderation_table.c.verification_date,
            orm.moderation_table.c.user_id,
            orm.moderation_table.c.reception_point_id,
        ).where(orm.moderation_table.c.id == id)

        result = await self._session.execute(stmt)
        row = result.mappings().first()

        if not row:
            return None

        row_dict = dict(row)

        return ModerationDTO(
            id=row_dict["id"],
            comment=row_dict.get("comment"),
            verification_date=row_dict["verification_date"],
            user_id=row_dict["user_id"],
            reception_point_id=row_dict["reception_point_id"],
        )

    async def get_all(self, filters: str | None = None) -> list[ModerationDTO]:
        stmt = select(
            orm.moderation_table,
            orm.moderation_table.c.comment,
            orm.moderation_table.c.verification_date,
            orm.moderation_table.c.user_id,
            orm.moderation_table.c.reception_point_id,
        )

        conditions = []

        if filters and filters != "null":
            try:
                criteria = dict(x.split("*") for x in filters.split("-"))
                for attr, value in criteria.items():
                    column = getattr(orm.moderation_table.c, attr, None)
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

        moderation_data_list = []
        for row in rows:
            row_dict = dict(row)
            moderation_data_list.append(
                ModerationDTO(
                    id=row_dict["id"],
                    comment=row_dict.get("comment"),
                    verification_date=row_dict["verification_date"],
                    user_id=row_dict["user_id"],
                    reception_point_id=row_dict["reception_point_id"],
                )
            )

        return moderation_data_list

    async def add(self, model: ModerationDTO) -> ModerationDTO:
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return model

    async def delete(self, id: uuid.UUID) -> None:
        stmt = delete(orm.moderation_table).where(orm.moderation_table.c.id == id)
        await self._session.execute(stmt)
        await self._session.commit()
