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

from app.adapters.postgres import PostgresUnitOfWork
from app.api.asgi import ASGI
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
def uow(db_engine: AsyncEngine, run_migration: None):
    return PostgresUnitOfWork(db_engine)


@pytest.fixture
def service(uow: PostgresUnitOfWork):
    return Service(uow)


@pytest.fixture
def asgi(service: Service):
    return ASGI(service, account_header="x-account-id")


@pytest_asyncio.fixture
async def client(asgi: ASGI):
    transport = httpx.ASGITransport(asgi)
    async with LifespanManager(asgi):
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            yield client
