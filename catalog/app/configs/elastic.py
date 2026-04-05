from pydantic_settings import BaseSettings


class ElasticConfig(BaseSettings):
    host: str = "http://127.0.0.1:9200"
    index: str = "catalog"
