import itertools
from unittest.mock import Mock

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from app.api.server import Server
from app.core.catalog import Catalog
from app.core.models import Furniture
from app.core.service import Service


@pytest.fixture
def catalog():
    return Mock(Catalog)


@pytest.fixture
def service(catalog: Catalog):
    return Service(catalog)


@pytest.fixture
def server(service: Service):
    return Server(service)


@pytest_asyncio.fixture
async def client(server: Server):
    transport = ASGITransport(server)
    async with LifespanManager(server):
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_furniture_by_id(client: AsyncClient, catalog: Mock):
    furniture = Furniture(
        id="test",
        name="test",
        width=1,
        height=1,
        depth=1,
        mount=Furniture.Mount.FLOOR,
        model_path="",
        icon_path="",
        thumbnail_path="",
        meta=Furniture.Meta(),
    )
    catalog.find.return_value = furniture

    resp = await client.get("/furniture/test")
    catalog.find.assert_called_once_with("test")
    assert resp.status_code == 200
    assert resp.json() == furniture.model_dump()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_furniture_by_id_not_found(client: AsyncClient, catalog: Mock):
    catalog.find.return_value = None

    resp = await client.get("/furniture/test")
    catalog.find.assert_called_once_with("test")
    assert resp.status_code == 404
    assert resp.json() == {"detail": "furniture not found"}


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["limit", "area", "cursor"],
    itertools.product(
        [1, 15, 20], [a.value for a in Furniture.Area] + [None], [None, "cursor"]
    ),
)
async def test_search_furniture(
    client: AsyncClient,
    catalog: Mock,
    area: Furniture.Area | None,
    limit: int,
    cursor: str | None,
):
    furniture = [
        Furniture(
            id="test",
            name="test",
            width=1,
            height=1,
            depth=1,
            mount=Furniture.Mount.FLOOR,
            model_path="",
            icon_path="",
            thumbnail_path="",
            meta=Furniture.Meta(),
        )
    ]
    catalog.search.return_value = (furniture, cursor)

    resp = await client.get(
        f"/search?limit={limit}" + (f"&area={area}" if area else "")
    )
    assert resp.status_code == 200
    assert resp.json() == {
        "furniture": list(map(lambda f: f.model_dump(), furniture)),
        "meta": {
            "cursor": cursor,
        },
    }


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["limit", "cursor"],
    itertools.product([1, 15, 20], [None, "cursor"]),
)
async def test_search_furniture_with_cursor(
    client: AsyncClient,
    catalog: Mock,
    cursor: str | None,
    limit: int,
):
    furniture = [
        Furniture(
            id="test",
            name="test",
            width=1,
            height=1,
            depth=1,
            mount=Furniture.Mount.FLOOR,
            model_path="",
            icon_path="",
            thumbnail_path="",
            meta=Furniture.Meta(),
        )
    ]
    catalog.get_next_search_result.return_value = (furniture, cursor)

    resp = await client.get(f"/search?cursor=test&limit={limit}")
    catalog.get_next_search_result.assert_called_once_with("test", limit)
    assert resp.status_code == 200
    assert resp.json() == {
        "furniture": list(map(lambda f: f.model_dump(), furniture)),
        "meta": {
            "cursor": cursor,
        },
    }


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["limit"],
    [[1], [15], [20]],
)
async def test_find_furniture_by_description(
    client: AsyncClient, catalog: Mock, limit: int
):
    furniture = [
        Furniture(
            id="test",
            name="test",
            width=1,
            height=1,
            depth=1,
            mount=Furniture.Mount.FLOOR,
            model_path="",
            icon_path="",
            thumbnail_path="",
            meta=Furniture.Meta(),
        )
    ]
    catalog.find_by_description.return_value = furniture

    resp = await client.get(f"/search/description?limit={limit}&description=test")
    catalog.find_by_description.assert_called_once_with("test", limit)
    assert resp.status_code == 200
    assert resp.json() == list(map(lambda f: f.model_dump(), furniture))


@pytest.mark.unit
@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 204
    assert resp.text == ""
