from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    api_prefix: str = "/api/v1"

    api_version: str = Field(validation_alias="WAVEO_API_VERSION")

    database_port: int = Field(validation_alias="DATABASE_PORT")

    postgres_db: str = Field(validation_alias="POSTGRES_DB")
    postgres_user: str = Field(validation_alias="POSTGRES_USER")
    postgres_password: str = Field(validation_alias="POSTGRES_PASSWORD")
    postgres_address: str = Field(validation_alias="POSTGRES_ADDRESS")

    @property
    def database_url_asyncpg(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_address}:{self.database_port}/{self.postgres_db}"
