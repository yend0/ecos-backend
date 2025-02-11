from dataclasses import dataclass

from pydantic import EmailStr
from pydantic_settings import BaseSettings

from jinja2 import Environment, PackageLoader, select_autoescape


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
    ECHO: bool = False

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


class S3Config(BaseSettings):
    S3_DOMAIN: str = "localhost"
    USER_BUCKET: str = "defaulrt_bucket"
    RECEPTION_POINT_BUCKET: str = "defaulrt_bucket"
    WASTE_BUCKET: str = "defaulrt_bucket"
    ENDPOINT: str = "http://localhost:9000"
    ACCESS_KEY: str = "admin"
    SECRET_KEY: str = "admin"


class SMTPConfig(BaseSettings):
    EMAIL_HOST: str = "localhost"
    EMAIL_PORT: int = 587
    EMAIL_USERNAME: str = "admin"
    EMAIL_PASSWORD: str = "admin"
    EMAIL_FROM: EmailStr = "admin@mail.com"


env_jinja2 = Environment(
    loader=PackageLoader("ecos_backend", "templates"),
    autoescape=select_autoescape(["html", "xml"]),
)

fastAPI_config: FastAPIConfig = FastAPIConfig()
database_config: DatabaseConfig = DatabaseConfig()
uvicorn_config: UvicornConfig = UvicornConfig()
keycloak_config: KeycloakConfig = KeycloakConfig()
s3_config: S3Config = S3Config()
smtp_config: SMTPConfig = SMTPConfig()
