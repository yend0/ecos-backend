from sqlalchemy.sql import func
from sqlalchemy import (
    ForeignKey,
    Table,
    Column,
    String,
    Date,
    DateTime,
    UUID,
    Integer,
    Time,
    Text,
    Enum,
)


from ecos_backend.db import mapper_registry
from ecos_backend.common import enums


user_table = Table(
    "User",
    mapper_registry.metadata,
    Column("id", UUID, primary_key=True, nullable=False, unique=True),
    Column("full_name", String(32), nullable=True, unique=False),
    Column("email", String(255), nullable=False, unique=True),
    Column("birth_date", Date, nullable=True),
    Column("image_url", String(255), nullable=True, unique=True),
    Column("verification_code", String(255), nullable=True),
    Column("points", Integer, nullable=False, default=0),
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

accrual_history_table = Table(
    "Accrual_History",
    mapper_registry.metadata,
    Column("id", UUID, primary_key=True, nullable=False, unique=True),
    Column("reward", Enum(enums.RewardType), nullable=False),
    Column("points", Integer, nullable=False),
    Column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
    Column(
        "user_id",
        UUID,
        ForeignKey("User.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    ),
)

work_schedule_table = Table(
    "Work_Schedule",
    mapper_registry.metadata,
    Column("id", UUID, primary_key=True, nullable=False, unique=True),
    Column("day_of_week", Enum(enums.Day), nullable=False),
    Column("open_time", Time, nullable=True),
    Column("close_time", Time, nullable=True),
    Column(
        "reception_point_id",
        UUID,
        ForeignKey("Reception_Point.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    ),
)

waste_table = Table(
    "Waste",
    mapper_registry.metadata,
    Column(
        "id",
        UUID,
        primary_key=True,
        nullable=False,
        unique=True,
    ),
    Column("name", String(32), nullable=False),
    Column("description", Text, nullable=False),
    Column("image_url", String(255), nullable=True, unique=True),
)

reception_point_table = Table(
    "Reception_Point",
    mapper_registry.metadata,
    Column("id", UUID, primary_key=True, nullable=False, unique=True),
    Column("name", String(255), nullable=False),
    Column("address", String(255), nullable=False, unique=True),
    Column("images_url", String(255), nullable=True, unique=True),
    Column(
        "updated_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    ),
    Column(
        "user_id",
        UUID,
        ForeignKey("User.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "status",
        Enum(enums.PointStatus),
        nullable=False,
        default=enums.PointStatus.UNDER_MODERATION,
    ),
)

drop_off_point_waste_table = Table(
    "Drop_Off_Point_Waste",
    mapper_registry.metadata,
    Column(
        "waste_id",
        ForeignKey("Waste.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "reception_point_id",
        ForeignKey("Reception_Point.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


def start_mappers() -> None:
    from ecos_backend.models.user import UserModel
    from ecos_backend.models.accrual_history import AccrualHistoryDTO
    from ecos_backend.models.drop_off_point_waste import DropOffPointWasteDTO
    from ecos_backend.models.reception_point import ReceptionPointDTO
    from ecos_backend.models.waste import WasteDTO
    from ecos_backend.models.work_schedule import WorkScheduleDTO

    mapper_registry.map_imperatively(
        class_=UserModel,
        local_table=user_table,
    )
    mapper_registry.map_imperatively(
        class_=AccrualHistoryDTO,
        local_table=accrual_history_table,
    )
    mapper_registry.map_imperatively(
        class_=WorkScheduleDTO,
        local_table=work_schedule_table,
    )
    mapper_registry.map_imperatively(
        class_=WasteDTO,
        local_table=waste_table,
    )
    mapper_registry.map_imperatively(
        class_=ReceptionPointDTO,
        local_table=reception_point_table,
    )
    mapper_registry.map_imperatively(
        class_=DropOffPointWasteDTO,
        local_table=drop_off_point_waste_table,
    )
