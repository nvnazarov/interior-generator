from abc import ABC, abstractmethod

from app.core.errors import FurnitureNotFoundError
from app.core.models import Cursor, Furniture, SearchResult

MAX_LIMIT = 20


class IFurnitureRepository(ABC):
    @abstractmethod
    async def get(self, furniture_id: str) -> Furniture | None: ...

    @abstractmethod
    async def search_with_cursor(self, cursor: Cursor, limit: int) -> SearchResult: ...

    @abstractmethod
    async def search(
        self, name: str | None, area: Furniture.Area | None, limit: int
    ) -> SearchResult: ...

    @abstractmethod
    async def get_top_k_like(self, k: int, description: str) -> list[Furniture]: ...


class Catalog:
    def __init__(self, furniture: IFurnitureRepository):
        self.furniture = furniture

    async def get_furniture_by_id(self, furniture_id: str) -> Furniture:
        furniture = await self.furniture.get(furniture_id)
        if furniture is None:
            raise FurnitureNotFoundError(f"furniture[id={furniture_id}] not found")
        return furniture

    async def search_furniture_with_cursor(
        self, cursor: Cursor, limit: int
    ) -> tuple[list[Furniture], Cursor | None]:
        return await self.furniture.search_with_cursor(cursor, min(limit, MAX_LIMIT))

    async def search_furniture(
        self, name: str | None, area: Furniture.Area | None, limit: int
    ) -> tuple[list[Furniture], Cursor | None]:
        return await self.furniture.search(name, area, min(limit, MAX_LIMIT))

    async def get_top_k_like(self, k: int, description: str) -> list[Furniture]:
        return await self.furniture.get_top_k_like(k, description)
