from abc import ABC, abstractmethod

from app.core.models import Prompt


class PromptsRepository(ABC):
    @abstractmethod
    async def in_project(self, project_id: str) -> list[Prompt]: ...

    @abstractmethod
    async def save(self, prompt: Prompt) -> None: ...

    @abstractmethod
    async def find(self, prompt_id: str) -> Prompt | None: ...

    @abstractmethod
    async def delete(self, prompt_id: str) -> None: ...
