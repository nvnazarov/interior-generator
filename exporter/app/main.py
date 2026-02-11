from httpx import AsyncClient

from app.adapters.external import ExternalPlansRepository
from app.api.api import API
from app.core.exporter import Exporter


def main():
    client = AsyncClient()
    repository = ProjectsServiceAdapter(client)
    exporter = Exporter(repository)
    api = API(exporter)

    api.run()


if __name__ == "__main__":
    main()
