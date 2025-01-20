from dataclasses import dataclass

from pydantic_settings import BaseSettings


@dataclass(frozen=True)
class URLPathsConfig:
    HOMEPAGE: str = "/"
    API_PREFIX: str = "/api"
    DOCS_URL: str = "/swagger-ui"
    REDOC_URL: str = "/redoc"


@dataclass(frozen=True)
class URLNamesConfig:
    HOMEPAGE: str = "homepage"


class FastAPIConfig(BaseSettings):
    TITLE: str = "Ecos REST API"
    DESCRIPTION: str = "REST API for Ecos project"
    API_VERSION: str = "0.0.0"


class DatabaseConfig(BaseSettings):
    DATABASE_PORT: int

    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_ADDRESS: str

    @property
    def database_url_asyncpg(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_ADDRESS}:{self.DATABASE_PORT}/{self.POSTGRES_DB}"


class UvicornConfig(BaseSettings):
    HOST: str = "localhost"
    PORT: int = 8000
    LOG_LEVEL: str = "info"
    RELOAD: bool = True
    FACTORY: bool = True


class KeycloakConfig(BaseSettings):
    KEYCLOAK_SERVER_URL: str = "http://localhost:8080/auth"
    KEYCLOAK_REALM: str = "master"
    KEYCLOAK_CLIENT_ID: str = "admin-cli"
    KEYCLOAK_CLIENT_SECRET: str = "secret"
    KEYCLOAK_ADMIN_NAME: str = "admin"
    KEYCLOAK_ADMIN_PASSWORD: str = "admin"
    KEYCLOAK_ADMIN_REALM: str = "master"


fastAPI_config: FastAPIConfig = FastAPIConfig()
database_config: DatabaseConfig = DatabaseConfig()
uvicorn_config: UvicornConfig = UvicornConfig()
keycloak_config: KeycloakConfig = KeycloakConfig()
