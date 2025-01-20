import abc

from ecos_backend.common.interfaces.repository import (
    AbstractRepository,
    AbstractSqlRepository,
)
from ecos_backend.domain.user import UserModel

from sqlalchemy.ext import asyncio


class UserAbstractReposity(AbstractRepository[UserModel], abc.ABC):
    pass


class UserReposity(AbstractSqlRepository[UserModel], UserAbstractReposity):
    def __init__(self, session: asyncio.AsyncSession) -> None:
        super().__init__(session, UserModel)
