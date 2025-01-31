from sqlalchemy import Table, Column, String, Date, UUID

from ecos_backend.db import mapper_registry

user_table = Table(
    "User",
    mapper_registry.metadata,
    Column("id", UUID, primary_key=True, nullable=False, unique=True),
    Column("full_name", String(32), nullable=True, unique=False),
    Column("email", String(255), nullable=False, unique=True),
    Column("birth_date", Date, nullable=True),
    Column("image_url", String(255), nullable=True, unique=True),
)


def start_mappers() -> None:
    from ecos_backend.domain.user import UserModel

    mapper_registry.map_imperatively(class_=UserModel, local_table=user_table)
