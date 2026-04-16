import logging

from app.core.db import PromptsRepository
from app.core.facade import SystemFacade
from app.core.generator import Generator
from app.core.models import Prompt

logger = logging.getLogger(__name__)

DEFAULT_PLANS_COUNT = 5


class ProjectNotFoundError(Exception): ...


class PlanNotFoundError(Exception): ...


class PromptNotFoundError(Exception): ...


class Server:
    def __init__(
        self, prompts: PromptsRepository, facade: SystemFacade, generator: Generator
    ):
        self.prompts = prompts
        self.facade = facade
        self.generator = generator

    async def generate_plans(
        self,
        account_id: str,
        project_id: str,
        text: str,
        base_plan_id: str | None = None,
        count: int = DEFAULT_PLANS_COUNT,
    ) -> Prompt:
        project = await self.facade.find_project(account_id, project_id)
        if project is None:
            raise ProjectNotFoundError
        base_plan = (
            None
            if base_plan_id is None
            else await self.facade.find_plan(account_id, base_plan_id)
        )
        if base_plan_id is not None and base_plan is None:
            raise PlanNotFoundError
        prompt = Prompt.create(
            project_id, text, base_plan.content if base_plan else None
        )
        await self.prompts.save(prompt)

        try:
            patches = await self.generator.generate_patches(project, base_plan, text, count)
            prompt.success(patches)
        except Exception as e:
            logger.error({"error": str(e)})
            prompt.fail()

        await self.prompts.save(prompt)
        return prompt

    async def get_prompts_for_project(
        self, account_id: str, project_id: str
    ) -> list[Prompt]:
        project = await self.facade.find_project(account_id, project_id)
        if project is None:
            raise ProjectNotFoundError
        return await self.prompts.get_for_project(project_id)

    async def delete_prompt(self, account_id: str, prompt_id: str):
        prompt = await self.prompts.get(prompt_id)
        if prompt is None:
            raise PromptNotFoundError
        project = await self.facade.find_project(account_id, prompt.project_id)
        if project is None:
            raise PromptNotFoundError
        await self.prompts.delete(prompt_id)
