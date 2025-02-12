import enum


class RewardType(enum.Enum):
    RECYCLE_POINT_ADD: str = "Добавлен пункт"


class PointStatus(enum.Enum):
    UNDER_MODERATION: str = "На модерации"
    APPROVED: str = "Одобрено"
    REJECTED: str = "Отклонено"
