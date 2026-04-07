from app.core.db import PromptsRepository
from app.core.models import Prompt


class PostgresPromptsRepository(PromptsRepository):
    async def get_prompts_for_project(self, project_id: str) -> list[Prompt]: ...
    async def save_prompt(self, prompt: Prompt) -> None: ...
