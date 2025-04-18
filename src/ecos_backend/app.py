import contextlib
import typing

import fastapi

from ecos_backend.common import config
from ecos_backend.api.v1.routers import root


@contextlib.asynccontextmanager
async def lifespan(_app: fastapi.FastAPI) -> typing.AsyncGenerator:
    """
    Runs events before application startup and after application shutdown.
    """

    yield


def create_app() -> fastapi.FastAPI:
    app: fastapi.FastAPI = fastapi.FastAPI(
        title=config.fastAPI_config.TITLE,
        description=config.fastAPI_config.DESCRIPTION,
        version=config.fastAPI_config.API_VERSION,
        docs_url=config.URLPathsConfig.DOCS_URL,
        redoc_url=config.URLPathsConfig.REDOC_URL,
        lifespan=lifespan,
    )

    app.include_router(router=root)

    return app
