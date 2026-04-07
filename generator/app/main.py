from app.adapters.gateway import GatewayFacade
from app.adapters.postgres import PostgresPromptsRepository
from app.api.asgi import ASGI
from app.configs.root import RootConfig
from app.core.server import Server


def main():
    config = RootConfig()
    facade = GatewayFacade()
    prompts = PostgresPromptsRepository()
    server = Server(prompts, facade)
    asgi = ASGI(server)
    asgi.listen_and_serve(config.api.host, config.api.port)


if __name__ == "__main__":
    main()
