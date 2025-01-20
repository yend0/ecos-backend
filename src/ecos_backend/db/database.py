from ecos_backend.common import config

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncEngine,
)


class DataBaseSQLHelper:
    def __init__(self, url: str, echo: bool = False) -> None:
        self._engine: AsyncEngine = create_async_engine(
            url=url,
            echo=echo,
        )

        self._session_factory: async_sessionmaker = async_sessionmaker(
            bind=self._engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    async def session_dependency(self):
        async with self._session_factory() as session:
            yield session
            await session.close()


dbSQLHelper: DataBaseSQLHelper = DataBaseSQLHelper(
    url=config.database_config.database_url_asyncpg,
    echo=True,
)
