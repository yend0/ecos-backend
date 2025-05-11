import abc

from ecos_backend.db.models.user_achievement import UserAchievement

from ecos_backend.common.interfaces.repository import (
    AbstractRepository,
    AbstractSqlRepository,
)


class UserAchievementAbstractReposity(AbstractRepository[UserAchievement], abc.ABC):
    pass


class UserAchievementReposity(
    AbstractSqlRepository[UserAchievement], UserAchievementAbstractReposity
):
    pass
