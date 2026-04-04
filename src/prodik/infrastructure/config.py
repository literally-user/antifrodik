from os import environ

from pydantic import BaseModel, Field


class APIConfig(BaseModel):
    host: str = Field(alias="API_HOST")
    port: int = Field(alias="API_PORT")


class DatabaseConfig(BaseModel):
    url: str = Field(alias="DATABASE_URL")


class SecretConfig(BaseModel):
    secret: str = Field(alias="SECRET")
    expires_in_seconds: int = Field(alias="EXPIRES_IN_SECONDS")


class Config(BaseModel):
    api_config: APIConfig = Field(default_factory=lambda: APIConfig(**environ))
    secret_config: SecretConfig = Field(default_factory=lambda: SecretConfig(**environ))
    database_config: DatabaseConfig = Field(
        default_factory=lambda: DatabaseConfig(**environ)
    )
