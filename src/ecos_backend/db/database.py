from ecos_backend.common import config

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncEngine,
)


class Database:
    def __init__(self, url: str, echo: bool = False) -> None:
        self._engine: AsyncEngine = create_async_engine(
            url=url,
            echo=echo,
            plugins=["geoalchemy2"],
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


def database_factory(config: config.DatabaseConfig) -> Database:
    return Database(
        url=config.database_url_asyncpg,
        echo=config.ECHO,
    )
