import abc

from ecos_backend.common.interfaces.repository import (
    AbstractRepository,
    AbstractSqlRepository,
)

from ecos_backend.db.models.waste import Waste


class WasteAbstractReposity(AbstractRepository[Waste], abc.ABC):
    pass


class WasteReposity(AbstractSqlRepository[Waste], WasteAbstractReposity):
    pass
