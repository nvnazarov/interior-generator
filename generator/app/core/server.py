from uuid import UUID

from app.core.db import PromptsRepository
from app.core.facade import SystemFacade
from app.core.models import Plan, Prompt

DEFAULT_PLANS_COUNT = 5


class Server:
    def __init__(self, prompts: PromptsRepository, facade: SystemFacade):
        self.prompts = prompts
        self.facade = facade

    async def generate_plans(
        self,
        account_id: str,
        project_id: str,
        base_plan_id: str | None = None,
        n: int = DEFAULT_PLANS_COUNT,
    ) -> list[Plan]:
        project = await self.facade.find_project(account_id, project_id)
        base_plan = (
            None
            if base_plan_id is None
            else await self.facade.find_plan(account_id, base_plan_id)
        )
        return []

    async def get_prompts_for_project(
        self, account_id: str, project_id: str
    ) -> list[Prompt]:
        return await self.prompts.get_prompts_for_project(project_id)
