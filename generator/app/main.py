from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from openai import AsyncOpenAI

from app.adapters.gateway import GatewayFacade
from app.adapters.postgres import PostgresPromptsRepository
from app.api.asgi import ASGI
from app.configs.root import RootConfig
from app.core.server import Server
from app.core.generator import Generator


def main():
    config = RootConfig()

    http_client = AsyncClient(base_url=config.gateway.base_url)
    sql_engine = create_async_engine(config.postgres.url())
    openai_client = AsyncOpenAI(
        api_key=config.openai.api_key,
        base_url=config.openai.base_url,
    )

    facade = GatewayFacade(http_client)
    prompts = PostgresPromptsRepository(sql_engine)
    generator = Generator(openai_client, facade)
    server = Server(prompts, facade, generator)
    asgi = ASGI(server)
    asgi.listen_and_serve(config.api.host, config.api.port)


if __name__ == "__main__":
    main()
