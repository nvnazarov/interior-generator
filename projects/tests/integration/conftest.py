import os
from pathlib import Path

import alembic.command
import alembic.config
import httpx
import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from testcontainers.postgres import PostgresContainer  # type: ignore

from app.adapters.postgres import PostgresUnitOfWorkFactory
from app.api.server import Server
from app.core.service import Service

os.environ["TESTCONTAINERS_RYUK_DISABLED"] = "true"


@pytest.fixture
def pyproject_toml():
    return Path(os.path.abspath(__file__)).parent.parent.parent / "pyproject.toml"


@pytest.fixture
def db_container():
    with PostgresContainer("postgres:17.5-alpine") as postgres:
        yield postgres


@pytest.fixture
def db_url(db_container: PostgresContainer):
    return db_container.get_connection_url(driver="psycopg")


@pytest.fixture
def db_engine(db_url: str):
    return create_async_engine(db_url)


@pytest_asyncio.fixture
async def run_migration(pyproject_toml: Path, db_url: str):
    revision = "head"
    config = alembic.config.Config(toml_file=pyproject_toml)
    config.attributes["sqlalchemy.url"] = db_url
    alembic.command.upgrade(config, revision)
    yield
    alembic.command.downgrade(config, "base")


@pytest.fixture
def uow_factory(db_engine: AsyncEngine, run_migration: None):
    return PostgresUnitOfWorkFactory(db_engine)


@pytest.fixture
def service(uow_factory: PostgresUnitOfWorkFactory):
    return Service(uow_factory)


@pytest.fixture
def server(service: Service):
    return Server(service, account_header="x-account-id")


@pytest_asyncio.fixture
async def client(server: Server):
    transport = httpx.ASGITransport(server)
    async with LifespanManager(server):
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            yield client
