import logging

from app.core.facade import SystemFacade
from app.core.generator import Generator
from app.core.models import Prompt
from app.core.repository import PromptsRepository

logger = logging.getLogger(__name__)


class ProjectNotFoundError(Exception): ...


class PlanNotFoundError(Exception): ...


class PromptNotFoundError(Exception): ...


class Service:
    def __init__(
        self, prompts: PromptsRepository, facade: SystemFacade, generator: Generator
    ):
        self._prompts = prompts
        self._facade = facade
        self._generator = generator

    async def create_prompt(
        self,
        *,
        account_id: str,
        project_id: str,
        text: str,
        count: int,
        base_plan_id: str | None = None,
    ) -> Prompt:
        project = await self._facade.find_project(account_id, project_id)
        if project is None:
            raise ProjectNotFoundError
        base_plan = (
            None
            if base_plan_id is None
            else await self._facade.find_plan(account_id, base_plan_id)
        )
        if base_plan_id is not None and base_plan is None:
            raise PlanNotFoundError
        prompt = Prompt.create(
            project_id, text, base_plan.content if base_plan else None
        )
        await self._prompts.save(prompt)

        try:
            patches = await self._generator.generate_patches(
                project, base_plan, text, count
            )
            prompt.success(patches)
        except Exception as e:
            logger.error({"error": str(e)})
            prompt.fail()

        await self._prompts.save(prompt)
        return prompt

    async def get_prompts_in_project(
        self, *, account_id: str, project_id: str
    ) -> list[Prompt]:
        project = await self._facade.find_project(account_id, project_id)
        if project is None:
            raise ProjectNotFoundError
        prompts = await self._prompts.in_project(project_id)
        return prompts

    async def delete_prompt(self, *, account_id: str, prompt_id: str):
        prompt = await self._prompts.find(prompt_id)
        if prompt is None:
            raise PromptNotFoundError
        project = await self._facade.find_project(account_id, prompt.project_id)
        if project is None:
            raise PromptNotFoundError
        await self._prompts.delete(prompt_id)
