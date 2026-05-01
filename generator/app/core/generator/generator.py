import logging

from openai import AsyncOpenAI

from app.core.facade import SystemFacade
from app.core.generator.context import GenerationContext
from app.core.models import Plan, Project

logger = logging.getLogger(__name__)


class Generator:
    def __init__(self, ai: AsyncOpenAI, facade: SystemFacade):
        self.ai = ai
        self.facade = facade

    async def generate_patches(
        self, project: Project, base_plan: Plan | None, text: str, count: int
    ) -> list[Plan.Patch]:
        context = GenerationContext(
            self.ai, self.facade, text, count, project, base_plan
        )
        patches = await context.generate_patches()
        return patches
