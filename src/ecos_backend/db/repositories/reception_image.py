import abc


from ecos_backend.db.models.reception_image import ReceptionImage

from ecos_backend.common.interfaces.repository import (
    AbstractRepository,
    AbstractSqlRepository,
)


class ReceptionImageAbstractReposity(AbstractRepository[ReceptionImage], abc.ABC):
    pass


class ReceptionImageReposity(
    AbstractSqlRepository[ReceptionImage], ReceptionImageAbstractReposity
):
    pass
