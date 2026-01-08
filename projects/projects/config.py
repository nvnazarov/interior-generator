from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisConfig(BaseSettings):
    host: str = "127.0.0.1"
    port: int = 6379
    db: int = 0


class PostgresConfig(BaseSettings):
    host: str = "127.0.0.1"
    port: int = 5432
    db: str
    user: str
    password: str = ""
    password_file: str | None = None

    def url(self):
        return f"postgres+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"

    def model_post_init(self, context: Any) -> None:
        if self.password_file is not None:
            with open(self.password_file, "r") as file:
                self.password = file.read()


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_", env_nested_delimiter="__")
    host: str = "127.0.0.1"
    port: int = 8080
    header_with_account_id: str = "x-account-id"
    max_projects_per_account: int = 20
    max_plans_per_project: int = 20
    postgres: PostgresConfig = Field(default_factory=PostgresConfig)
