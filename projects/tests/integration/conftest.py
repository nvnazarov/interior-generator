import os
from pathlib import Path

from httpx import AsyncClient, ASGITransport
import pytest_asyncio
from testcontainers.postgres import PostgresContainer
from alembic.config import Config
from alembic import command
from asgi_lifespan import LifespanManager

from projects.api import API
from projects.core.service import ProjectService
from projects.infra.uow import ProjectUnitOfWorkFactory


PYPROJECT_TOML = Path(os.path.abspath(__file__)).parent.parent.parent / "pyproject.toml"


@pytest_asyncio.fixture(scope="function")
async def api():
    with PostgresContainer("postgres:17.5-alpine") as postgres:
        config = Config(toml_file=PYPROJECT_TOML)
        config.set_main_option(
            "sqlalchemy.url", postgres.get_connection_url(driver="psycopg")
        )
        command.upgrade(config, "head")

        url = postgres.get_connection_url(driver="asyncpg")
        uow_factory = ProjectUnitOfWorkFactory(url)
        project_service = ProjectService(uow_factory, max_projects_per_account=20)
        api = API(project_service, header_with_account_id="x-account-id")
        yield api


@pytest_asyncio.fixture(scope="function")
async def client(api: API):
    app = api.asgi()
    transport = ASGITransport(app)
    async with LifespanManager(app):
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client
