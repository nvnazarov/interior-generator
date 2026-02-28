from pydantic_settings import BaseSettings


class APIConfig(BaseSettings):
    host: str = "127.0.0.1"
    port: int = 8080
    header_for_account_id: str = "x-account-id"
