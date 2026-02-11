from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="app_", env_nested_delimiter="__")
    host: str = "127.0.0.1"
    port: int = 8080
    header_for_account_id: str = "x-account-id"

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
