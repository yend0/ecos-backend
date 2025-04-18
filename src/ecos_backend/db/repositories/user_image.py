import abc

from ecos_backend.common.interfaces.repository import (
    AbstractRepository,
    AbstractSqlRepository,
)

from ecos_backend.db.models.user_image import UserImage


class UserImageAbstractReposity(AbstractRepository[UserImage], abc.ABC):
    pass


class UserImageReposity(AbstractSqlRepository[UserImage], UserImageAbstractReposity):
    pass
