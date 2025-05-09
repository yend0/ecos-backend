import abc


from ecos_backend.db.models.waste_translation import WasteTranslation

from ecos_backend.common.interfaces.repository import (
    AbstractRepository,
    AbstractSqlRepository,
)


class WasteTranslationAbstractReposity(AbstractRepository[WasteTranslation], abc.ABC):
    pass


class WasteTranslationReposity(
    AbstractSqlRepository[WasteTranslation], WasteTranslationAbstractReposity
):
    pass
