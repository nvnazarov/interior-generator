import os
from pathlib import Path
from uuid import uuid4

import alembic.command
import alembic.config
import httpx
import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from sqlalchemy.ext.asyncio import create_async_engine
from testcontainers.postgres import PostgresContainer  # type: ignore

from app.adapters.postgres import PostgresFurnitureRepository
from app.api.asgi import ASGI
from app.core.catalog import Catalog, IFurnitureRepository
from app.core.models import Furniture


@pytest.fixture
def pyproject_toml():
    return Path(os.path.abspath(__file__)).parent.parent / "pyproject.toml"


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
def repository(db_url: str, run_migration: None):
    engine = create_async_engine(db_url)
    return PostgresFurnitureRepository(engine)


@pytest.fixture
def catalog(repository: IFurnitureRepository):
    return Catalog(repository)


@pytest.fixture
def asgi(catalog: Catalog):
    return ASGI(catalog)


@pytest_asyncio.fixture
async def client(asgi: ASGI):
    transport = httpx.ASGITransport(asgi)
    async with LifespanManager(asgi):
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            yield client


@pytest.fixture
def furniture_gen():
    def generator():
        while True:
            yield Furniture(
                id=uuid4(),
                name=str(uuid4()),
                width=10,
                height=11,
                depth=12,
                mount=Furniture.Mount.FLOOR,
                model_path="/models/test.obj",
                icon_path="/icons/test.png",
                thumbnail_path="/thumbnails/test.png",
                meta=Furniture.Meta(
                    area=Furniture.Area.KITCHEN,
                    function=Furniture.Function.DINING,
                ),
            )

    return generator()
