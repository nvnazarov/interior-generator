from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.configs.api import APIConfig
from app.configs.gateway import GatewayConfig
from app.configs.logging import LoggingConfig


class RootConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="exporter__",
        env_nested_delimiter="__",
    )
    api: APIConfig = Field(default_factory=APIConfig)
    api_gateway: GatewayConfig = Field(default_factory=GatewayConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
