from unittest.mock import Mock

import httpx
import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager

from app.api.server import Server
from app.core.catalog import Catalog
from app.core.exporter import Exporter
from app.core.projects import ProjectsService


@pytest.fixture
def catalog():
    return Mock(Catalog)


@pytest.fixture
def projects():
    return Mock(ProjectsService)


@pytest.fixture
def exporter(catalog: Mock, projects: Mock):
    return Exporter(projects, catalog)


@pytest.fixture
def server(exporter: Exporter):
    return Server(exporter)


@pytest_asyncio.fixture
async def client(server: Server):
    transport = httpx.ASGITransport(server)
    async with LifespanManager(server):
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            yield client
