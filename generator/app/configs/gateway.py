from pydantic_settings import BaseSettings


class GatewayConfig(BaseSettings):
    base_url: str = ""
