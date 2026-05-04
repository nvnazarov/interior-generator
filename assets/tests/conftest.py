from unittest.mock import Mock

import httpx
import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager

from app.api.server import Server
from app.core.service import Service
from app.core.storage import Storage


@pytest.fixture
def storage():
    return Mock(Storage)


@pytest.fixture
def service(storage: Mock):
    return Service(storage)


@pytest.fixture
def server(service: Service):
    return Server(service)


@pytest_asyncio.fixture
async def client(server: Server):
    transport = httpx.ASGITransport(server)
    async with LifespanManager(server):
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            yield client
