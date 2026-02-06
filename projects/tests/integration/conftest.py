import os
from pathlib import Path

import alembic.command
import alembic.config
import httpx
import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from sqlalchemy.ext.asyncio import create_async_engine
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
def run_migration(pyproject_toml: Path, db_url: str):
    revision = "head"
    config = alembic.config.Config(toml_file=pyproject_toml)
    config.set_main_option("sqlalchemy.url", db_url)
    alembic.command.upgrade(config, revision)
    yield
    alembic.command.downgrade(config, "base")


@pytest.fixture
def uow(db_url: str, run_migration: None):
    engine = create_async_engine(db_url)
    return PostgresUnitOfWork(engine)


@pytest.fixture
def service(uow: PostgresUnitOfWork):
    return Service(uow)


@pytest.fixture
def asgi(service: Service):
    return ASGI(service, header_for_account_id="x-account-id")


@pytest_asyncio.fixture
async def client(asgi: ASGI):
    transport = httpx.ASGITransport(asgi)
    async with LifespanManager(asgi):
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            yield client
