import abc


from ecos_backend.common.interfaces.repository import (
    AbstractRepository,
    AbstractSqlRepository,
)

from ecos_backend.db.models.moderation import Moderation


class ModerationAbstractReposity(AbstractRepository[Moderation], abc.ABC):
    pass


class ModerationReposity(AbstractSqlRepository[Moderation], ModerationAbstractReposity):
    pass
