from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.configs.api import APIConfig
from app.configs.general import GeneralConfig
from app.configs.postgres import PostgresConfig
from app.configs.logging import LoggingConfig


class RootConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="projects__",
        env_nested_delimiter="__",
    )
    api: APIConfig = Field(default_factory=APIConfig)
    general: GeneralConfig = Field(default_factory=GeneralConfig)
    postgres: PostgresConfig = Field(default_factory=PostgresConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
