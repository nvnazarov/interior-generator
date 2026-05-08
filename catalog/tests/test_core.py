import itertools
from unittest.mock import Mock

import pytest

from app.core.catalog import Catalog
from app.core.models import Furniture
from app.core.service import FurnitureNotFoundError, Service


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["limit", "area", "cursor"],
    itertools.product(
        [1, 15, 30], [a.value for a in Furniture.Area] + [None], [None, "cursor"]
    ),
)
async def test_search_furniture(
    area: Furniture.Area | None, limit: int, cursor: str | None
):
    catalog = Mock(Catalog)
    service = Service(catalog)
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

    result = await service.search_furniture("test-name", area, limit)
    catalog.search.assert_called_once_with("test-name", area, min(20, limit))
    assert result[0] == furniture
    assert result[1] == cursor


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["limit", "cursor"],
    itertools.product([1, 15, 30], [None, "cursor"]),
)
async def test_get_next_search_result(limit: int, cursor: str | None):
    catalog = Mock(Catalog)
    service = Service(catalog)
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

    result = await service.get_next_search_result("test-cursor", limit)
    catalog.get_next_search_result.assert_called_once_with(
        "test-cursor", min(20, limit)
    )
    assert result[0] == furniture
    assert result[1] == cursor


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_furniture_by_id():
    catalog = Mock(Catalog)
    service = Service(catalog)
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

    result = await service.get_furniture_by_id("test")
    catalog.find.assert_called_once_with("test")
    assert result == furniture


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_furniture_by_id_not_found():
    catalog = Mock(Catalog)
    service = Service(catalog)
    catalog.find.return_value = None

    with pytest.raises(FurnitureNotFoundError):
        _ = await service.get_furniture_by_id("test")
    catalog.find.assert_called_once_with("test")


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["limit"],
    [[1], [15], [30]],
)
async def test_find_furniture_by_description(limit: int):
    catalog = Mock(Catalog)
    service = Service(catalog)
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

    result = await service.find_furniture_by_description("test", limit)
    catalog.find_by_description.assert_called_once_with("test", min(20, limit))
    assert result == furniture
