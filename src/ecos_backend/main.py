import uvicorn

from ecos_backend.common import config

if __name__ == "__main__":
    uvicorn.run(
        "ecos_backend.app:create_app",
        host=config.uvicorn_config.HOST,
        port=config.uvicorn_config.PORT,
        factory=config.uvicorn_config.FACTORY,
        reload=config.uvicorn_config.RELOAD,
        log_level=config.uvicorn_config.LOG_LEVEL,
    )
