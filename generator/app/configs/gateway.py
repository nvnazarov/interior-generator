from pydantic_settings import BaseSettings


class GatewayConfig(BaseSettings):
    base_url: str = "http://localhost:8080/api"
