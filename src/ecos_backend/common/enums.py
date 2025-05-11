import enum


class Status(enum.Enum):
    SUCCESS: str = "SUCCESS"
    FAILURE: str = "FAILURE"


class RewardType(enum.Enum):
    RECYCLE_POINT_ADD: str = "Добавлен пункт"


class PointStatus(enum.Enum):
    UNDER_MODERATION: str = "На модерации"
    APPROVED: str = "Одобрено"
    REJECTED: str = "Отклонено"


class AchievementType(enum.Enum):
    FIRST_CONTRIBUTION = "first_contribution"
    FIVE_CONTRIBUTIONS = "five_contributions"
    TEN_CONTRIBUTIONS = "ten_contributions"
    ECO_CHAMPION = "eco_champion"
    MAP_MAKER = "map_maker"


class DayOfWeek(enum.Enum):
    MONDAY: int = 1
    TUESDAY: int = 2
    WEDNESDAY: int = 3
    THURSDAY: int = 4
    FRIDAY: int = 5
    SATURDAY: int = 6
    SUNDAY: int = 7


class LanguageCode(enum.Enum):
    RU = "ru"
    EN = "en"
