from typing import Any

from pydantic_settings import BaseSettings


class OpenAIConfig(BaseSettings):
    api_key: str = ""
    api_key_file: str | None = None
    base_url: str = ""

    def model_post_init(self, context: Any) -> None:
        if self.api_key_file is not None:
            with open(self.api_key_file, "r") as file:
                self.api_key = file.read()
