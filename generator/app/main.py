from httpx import AsyncClient
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import create_async_engine

from app.adapters.gateway import GatewayFacade
from app.adapters.postgres import PostgresPromptsRepository
from app.api.server import Server
from app.configs.root import RootConfig
from app.core.generator import Generator
from app.core.service import Service


def main():
    config = RootConfig()

    http_client = AsyncClient(base_url=config.gateway.base_url)
    sql_engine = create_async_engine(config.postgres.url())
    openai_client = AsyncOpenAI(
        api_key=config.openai.api_key,
        base_url=config.openai.base_url,
    )

    facade = GatewayFacade(http_client, config.api.account_header)
    prompts = PostgresPromptsRepository(sql_engine)
    generator = Generator(openai_client, facade)
    service = Service(prompts, facade, generator)
    server = Server(service, config.api.account_header)
    server.listen_and_serve(config.api.host, config.api.port)


if __name__ == "__main__":
    main()
