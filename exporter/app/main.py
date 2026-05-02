from httpx import AsyncClient

from app.adapters.gateway import GatewayCatalog, GatewayProjectsService
from app.api.asgi import ASGI
from app.configs.root import RootConfig
from app.core.exporter import Exporter


def main():
    config = RootConfig()
    client = AsyncClient(base_url=config.gateway.base_url)
    catalog = GatewayCatalog(client)
    projects = GatewayProjectsService(client)
    exporter = Exporter(projects, catalog)
    asgi = ASGI(exporter, account_header=config.api.account_header)
    asgi.listen_and_serve(config.api.host, config.api.port)


if __name__ == "__main__":
    main()
