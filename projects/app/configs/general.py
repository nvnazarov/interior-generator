from pydantic_settings import BaseSettings


class GeneralConfig(BaseSettings):
    projects_limit: int = 20
    plans_limit: int = 20
