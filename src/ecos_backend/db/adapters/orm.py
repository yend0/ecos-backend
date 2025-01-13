from sqlalchemy import Table, Column, String, Date, UUID

from ecos_backend.db import mapper_registry

users_table = Table(
    "users",
    mapper_registry.metadata,
    Column("id", UUID, primary_key=True, nullable=False, unique=True),
    Column("email", String, nullable=False, unique=True),
    Column("full_name", String, nullable=True, unique=False),
    Column("birth_date", Date, nullable=True),
    Column("image_url", String, nullable=True),
)


def start_mappers() -> None:
    from ecos_backend.domain.user import UserModel

    mapper_registry.map_imperatively(class_=UserModel, local_table=users_table)
