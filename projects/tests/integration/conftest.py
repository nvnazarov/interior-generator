import os
from pathlib import Path

import pytest_asyncio
from alembic import command
from alembic.config import Config
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from testcontainers.postgres import PostgresContainer

from app.api import API
from app.api.idempotency import IdempotencyProvider
from app.core.plan.service import PlanService
from app.core.project.service import ProjectService
from app.core.shell.service import ShellService
from app.infra.plan import PlansUnitOfWork
from app.infra.project import ProjectsUnitOfWork
from app.infra.shell import ShellsUnitOfWork

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
        engine = create_async_engine(url)
        api = API(
            plan_service=PlanService(
                lambda: PlansUnitOfWork(engine),
                max_plans_per_project=20,
            ),
            shell_service=ShellService(
                lambda: ShellsUnitOfWork(engine),
                max_shells_per_account=20,
            ),
            project_service=ProjectService(
                lambda: ProjectsUnitOfWork(engine),
                max_projects_per_account=20,
            ),
            idempotency_provider=IdempotencyProvider(),
            header_with_account_id="x-account-id",
        )
        yield api


@pytest_asyncio.fixture(scope="function")
async def client(api: API):
    app = api.asgi()
    transport = ASGITransport(app)
    async with LifespanManager(app):
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client
