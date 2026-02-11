from abc import ABC, abstractmethod
from io import BytesIO
from typing import AsyncIterable
from uuid import UUID

from app.core.dxf import DXFRenderer
from app.core.models import Plan, Project
from app.core.pdf import PDFRenderer


class ProjectNotFoundError(Exception): ...


class PlanNotFoundError(Exception): ...


async def export_pdf(project: Project, plans: AsyncIterable[Plan]) -> BytesIO:
    buffer = BytesIO()
    renderer = PDFRenderer(buffer)
    async for plan in plans:
        renderer.draw_plan(plan)
    renderer.close()
    buffer.seek(0)
    return buffer


def export_dxf(project: Project, plan: Plan) -> BytesIO:
    buffer = BytesIO()
    renderer = DXFRenderer(buffer)
    # TODO(nvnazarov@edu.hse.ru): use renderer to render a plan
    renderer.flush()
    buffer.seek(0)
    return buffer


class ProjectRepository(ABC):
    @abstractmethod
    async def get(self, account_id: UUID, project_id: UUID) -> Project | None: ...


class PlanRepository(ABC):
    @abstractmethod
    async def get(self, account_id: UUID, plan_id: UUID) -> Plan | None: ...

    @abstractmethod
    async def get_of_project(
        self, account_id: UUID, project_id: UUID
    ) -> AsyncIterable[Plan]: ...


class Exporter:
    def __init__(self, projects: ProjectRepository, plans: PlanRepository):
        self.projects = projects
        self.plans = plans

    async def export_pdf(self, project_id: UUID, account_id: UUID) -> BytesIO:
        project = await self.projects.get(account_id, project_id)
        if project is None:
            raise ProjectNotFoundError
        plans = await self.plans.get_of_project(account_id, project_id)
        bytes = await export_pdf(project, plans)
        return bytes

    async def export_dxf(self, plan_id: UUID, account_id: UUID) -> BytesIO:
        plan = await self.plans.get(account_id, plan_id)
        if plan is None:
            raise PlanNotFoundError
        project = await self.projects.get(account_id, plan.project_id)
        if project is None:
            raise RuntimeError("plan exists but its project does not")
        bytes = export_dxf(project, plan)
        return bytes
