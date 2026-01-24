from uuid import uuid4

import pytest
from fastapi import status
from httpx import AsyncClient

from app.core.catalog import Catalog
from app.core.models import Furniture


@pytest.mark.asyncio
async def test_get_furniture_by_id(client: AsyncClient, catalog: Catalog):
    resp = await client.get("/furniture/1")
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    resp = await client.get(f"/furniture/{uuid4()}")
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json() == {"detail": "furniture not found"}

    furniture = Furniture(
        id=uuid4(),
        name="test",
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
    await catalog.add_furniture(furniture)

    resp = await client.get(f"/furniture/{furniture.id.hex}")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == furniture.model_dump(mode="json")


@pytest.mark.asyncio
async def test_search_furniture(client: AsyncClient, catalog: Catalog):
    chair = Furniture(
        id=uuid4(),
        name="chair",
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
    toilet = Furniture(
        id=uuid4(),
        name="toilet",
        width=10,
        height=11,
        depth=12,
        mount=Furniture.Mount.FLOOR,
        model_path="/models/test.obj",
        icon_path="/icons/test.png",
        thumbnail_path="/thumbnails/test.png",
        meta=Furniture.Meta(
            area=Furniture.Area.BATHROOM,
            function=Furniture.Function.RELAX,
        ),
    )
    await catalog.add_furniture(chair)
    await catalog.add_furniture(toilet)

    resp = await client.get(f"/search?area={Furniture.Area.KITCHEN}")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["furniture"] == [chair.model_dump(mode="json")]

    resp = await client.get(f"/search?area={Furniture.Area.BATHROOM}")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["furniture"] == [toilet.model_dump(mode="json")]

    resp = await client.get(f"/search?area={Furniture.Area.BEDROOM}")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["furniture"] == []

    resp = await client.get("/search?name=toi")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["furniture"] == [toilet.model_dump(mode="json")]

    resp = await client.get("/search?name=air")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["furniture"] == [chair.model_dump(mode="json")]


@pytest.mark.asyncio
async def test_search_furniture_with_cursor(client: AsyncClient, catalog: Catalog):
    for _ in range(10):
        furniture = Furniture(
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
        await catalog.add_furniture(furniture)
    for _ in range(10):
        furniture = Furniture(
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
                area=Furniture.Area.BATHROOM,
                function=Furniture.Function.RELAX,
            ),
        )
        await catalog.add_furniture(furniture)

    cursor: str | None = None
    for _ in range(5):
        resp = await client.get(
            f"/search?area={Furniture.Area.KITCHEN}&limit=2"
            if cursor is None
            else f"/search?cursor={cursor}&limit=2"
        )
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.json()["furniture"]) == 2
        assert (cursor := resp.json()["meta"]["cursor"]) is not None

    resp = await client.get(f"/search?cursor={cursor}&limit=2")
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.json()["furniture"]) == 0
    assert resp.json()["meta"]["cursor"] is None
