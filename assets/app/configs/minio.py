from typing import Any

from pydantic_settings import BaseSettings


class MinioConfig(BaseSettings):
    host: str = "127.0.0.1"
    port: int = 9000
    access_key: str = ""
    secret_key: str = ""
    secret_key_file: str | None = None

    def model_post_init(self, context: Any) -> None:
        if self.secret_key_file is not None:
            with open(self.secret_key_file, "r") as file:
                self.secret_key = file.read()
