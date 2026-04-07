from abc import ABC, abstractmethod

from app.core.models import Prompt


class PromptsRepository(ABC):
    @abstractmethod
    async def get_prompts_for_project(self, project_id: str) -> list[Prompt]: ...
    @abstractmethod
    async def save_prompt(self, prompt: Prompt) -> None: ...
