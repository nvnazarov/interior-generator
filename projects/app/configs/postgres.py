from typing import Any

from pydantic_settings import BaseSettings


class PostgresConfig(BaseSettings):
    host: str = "127.0.0.1"
    port: int = 5432
    db: str = "postgres"
    user: str = "postgres"
    password: str = ""
    password_file: str | None = None

    def url(self):
        return f"postgresql+psycopg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"

    def model_post_init(self, context: Any) -> None:
        if self.password_file is not None:
            with open(self.password_file, "r") as file:
                self.password = file.read()
