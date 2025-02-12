import enum


class RewardType(enum.Enum):
    RECYCLE_POINT_ADD: str = "Добавлен пункт"


class PointStatus(enum.Enum):
    UNDER_MODERATION: str = "На модерации"
    APPROVED: str = "Одобрено"
    REJECTED: str = "Отклонено"


class Day(enum.Enum):
    MONDAY: int = 1
    TYESDAY: int = 2
    WEDNESDAY: int = 3
    THURSDAY: int = 4
    FRIDAY: int = 5
    SATURDAY: int = 6
    SUNDAY: int = 7
