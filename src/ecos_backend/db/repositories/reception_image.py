import abc

from ecos_backend.common.interfaces.repository import (
    AbstractRepository,
    AbstractSqlRepository,
)

from ecos_backend.db.models.reception_image import ReceptionImage


class ReceptionImageAbstractReposity(AbstractRepository[ReceptionImage], abc.ABC):
    pass


class ReceptionImageReposity(
    AbstractSqlRepository[ReceptionImage], ReceptionImageAbstractReposity
):
    pass
