from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.configs.api import APIConfig
from app.configs.logging import LoggingConfig
from app.configs.postgres import PostgresConfig


class RootConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="catalog__",
        env_nested_delimiter="__",
    )
    api: APIConfig = Field(default_factory=APIConfig)
    postgres: PostgresConfig = Field(default_factory=PostgresConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
