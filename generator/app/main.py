from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine

from app.adapters.gateway import GatewayFacade
from app.adapters.postgres import PostgresPromptsRepository
from app.api.asgi import ASGI
from app.configs.root import RootConfig
from app.core.server import Server


def main():
    config = RootConfig()
    http_client = AsyncClient(base_url=config.gateway.base_url)
    facade = GatewayFacade(http_client)
    sql_engine = create_async_engine(config.postgres.url())
    prompts = PostgresPromptsRepository(sql_engine)
    server = Server(prompts, facade)
    asgi = ASGI(server)
    asgi.listen_and_serve(config.api.host, config.api.port)


if __name__ == "__main__":
    main()
