from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresConfig(BaseSettings):
    host: str = "127.0.0.1"
    port: int = 5432
    db: str
    user: str
    password: str = ""
    password_file: str | None = None

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

    def url(self):
        return f"postgresql+psycopg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"

    def model_post_init(self, context: Any) -> None:
        if self.password_file is not None:
            with open(self.password_file, "r") as file:
                self.password = file.read()


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="app_", env_nested_delimiter="__")

    host: str = "127.0.0.1"
    port: int = 8080
    postgres: PostgresConfig = Field(default_factory=PostgresConfig)
