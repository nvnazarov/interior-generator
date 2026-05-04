from abc import ABC, abstractmethod

from app.core.models import Cursor, Furniture, SearchResult


class Catalog(ABC):
    @abstractmethod
    async def find(self, furniture_id: str) -> Furniture | None: ...

    @abstractmethod
    async def get_next_search_result(
        self, cursor: Cursor, limit: int
    ) -> SearchResult: ...

    @abstractmethod
    async def search(
        self, name: str | None, area: Furniture.Area | None, limit: int
    ) -> SearchResult: ...

    @abstractmethod
    async def find_by_description(
        self, description: str, limit: int
    ) -> list[Furniture]: ...
