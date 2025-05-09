import abc


from ecos_backend.db.models.user_image import UserImage

from ecos_backend.common.interfaces.repository import (
    AbstractRepository,
    AbstractSqlRepository,
)


class UserImageAbstractReposity(AbstractRepository[UserImage], abc.ABC):
    pass


class UserImageReposity(AbstractSqlRepository[UserImage], UserImageAbstractReposity):
    pass
