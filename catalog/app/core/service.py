from app.core.catalog import Catalog
from app.core.models import Cursor, Furniture, SearchResult

MAX_LIMIT = 20


class FurnitureNotFoundError(Exception):
    pass


class Service:
    def __init__(self, catalog: Catalog):
        self._catalog = catalog

    async def get_furniture_by_id(self, furniture_id: str) -> Furniture:
        furniture = await self._catalog.find(furniture_id)
        if furniture is None:
            raise FurnitureNotFoundError(f"furniture[id={furniture_id}] not found")
        return furniture

    async def get_next_search_result(self, cursor: Cursor, limit: int) -> SearchResult:
        limit = min(limit, MAX_LIMIT)
        return await self._catalog.get_next_search_result(cursor, limit)

    async def search_furniture(
        self, name: str | None, area: Furniture.Area | None, limit: int
    ) -> SearchResult:
        limit = min(limit, MAX_LIMIT)
        return await self._catalog.search(name, area, limit)

    async def find_furniture_by_description(
        self, description: str, limit: int
    ) -> list[Furniture]:
        limit = min(limit, MAX_LIMIT)
        return await self._catalog.find_by_description(description, limit)
