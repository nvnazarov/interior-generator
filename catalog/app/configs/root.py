from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.configs.api import APIConfig
from app.configs.elastic import ElasticConfig
from app.configs.logging import LoggingConfig


class RootConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="catalog__",
        env_nested_delimiter="__",
    )
    api: APIConfig = Field(default_factory=APIConfig)
    elastic: ElasticConfig = Field(default_factory=ElasticConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
