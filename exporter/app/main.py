from httpx import AsyncClient

from app.api.api import API
from app.core.exporter import Exporter
from app.infra.projects_service import ProjectsServiceAdapter


def main():
    client = AsyncClient()
    repository = ProjectsServiceAdapter(client)
    exporter = Exporter(repository)
    api = API(exporter)

    api.run()


if __name__ == "__main__":
    main()
