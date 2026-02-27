from app.api.asgi import ASGI
from app.configs.root import RootConfig
from app.core.server import Server


def main():
    config = RootConfig()
    server = Server()
    asgi = ASGI(server)
    asgi.listen_and_serve(config.api.host, config.api.port)


if __name__ == "__main__":
    main()
