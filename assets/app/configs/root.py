from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.configs.api import APIConfig
from app.configs.logging import LoggingConfig
from app.configs.minio import MinioConfig


class RootConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="assets__",
        env_nested_delimiter="__",
    )
    api: APIConfig = Field(default_factory=APIConfig)
    minio: MinioConfig = Field(default_factory=MinioConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
