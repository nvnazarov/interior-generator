from httpx import AsyncClient

from app.adapters.gateway import APIGatewayAdapter
from app.api.asgi import ASGI
from app.configs.root import RootConfig
from app.core.exporter import Exporter


def main():
    config = RootConfig()
    client = AsyncClient(base_url=config.api_gateway.base_url)
    gateway = APIGatewayAdapter(client)
    exporter = Exporter(gateway)
    asgi = ASGI(exporter, header_for_account_id=config.api.header_for_account_id)
    asgi.listen_and_serve(config.api.host, config.api.port)


if __name__ == "__main__":
    main()
