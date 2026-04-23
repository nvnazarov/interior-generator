from typing import Awaitable
from abc import ABC, abstractmethod
from app.core.models import Furniture


class Catalog(ABC):
    @abstractmethod
    def find_furniture_by_id(self, id: str) -> Awaitable[Furniture | None]: ...
