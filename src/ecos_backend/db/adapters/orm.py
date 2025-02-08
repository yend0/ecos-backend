from sqlalchemy import Table, Column, String, Date, DateTime, UUID
from sqlalchemy.sql import func

from ecos_backend.db import mapper_registry

user_table = Table(
    "User",
    mapper_registry.metadata,
    Column("id", UUID, primary_key=True, nullable=False, unique=True),
    Column("full_name", String(32), nullable=True, unique=False),
    Column("email", String(255), nullable=False, unique=True),
    Column("birth_date", Date, nullable=True),
    Column("image_url", String(255), nullable=True, unique=True),
    Column("verification_code", String(255), nullable=True),
    Column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
    Column(
        "updated_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    ),
    Column(
        "verification_code_created_at",
        DateTime(timezone=True),
        nullable=True,
    ),
)


def start_mappers() -> None:
    from ecos_backend.domain.user import UserModel

    mapper_registry.map_imperatively(class_=UserModel, local_table=user_table)
