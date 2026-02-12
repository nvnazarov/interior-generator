from httpx import AsyncClient

from app.adapters.external import ExternalRepository
from app.api.asgi import ASGI
from app.config import Config
from app.core.exporter import Exporter


def main():
    config = Config()
    client = AsyncClient(base_url=config.repo_base_url)
    repository = ExternalRepository(client)
    exporter = Exporter(repository)
    asgi = ASGI(exporter, header_for_account_id=config.header_for_account_id)
    asgi.run(config.host, config.port)


if __name__ == "__main__":
    main()
