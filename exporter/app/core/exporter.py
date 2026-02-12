from abc import ABC, abstractmethod
from io import BytesIO
from typing import AsyncIterable
from uuid import UUID

from app.core.dxf import export_dxf
from app.core.models import Plan, Project
from app.core.pdf import export_pdf


class ProjectNotFoundError(Exception): ...


class PlanNotFoundError(Exception): ...


class Catalog(ABC):
    @abstractmethod
    async def get_furniture(self, furniture_id: UUID) -> None: ...


class Repository(ABC):
    @abstractmethod
    async def get_project(
        self, account_id: UUID, project_id: UUID
    ) -> Project | None: ...

    @abstractmethod
    async def get_plan(self, account_id: UUID, plan_id: UUID) -> Plan | None: ...

    @abstractmethod
    def get_plans_of_project(
        self, account_id: UUID, project_id: UUID
    ) -> AsyncIterable[Plan]: ...


class Exporter:
    def __init__(self, db: Repository):
        self.db = db

    async def export_project_pdf(self, project_id: UUID, account_id: UUID) -> BytesIO:
        project = await self.db.get_project(account_id, project_id)
        if project is None:
            raise ProjectNotFoundError
        plans = self.db.get_plans_of_project(account_id, project_id)
        bytes = await export_pdf(project, plans)
        return bytes

    async def export_plan_dxf(self, plan_id: UUID, account_id: UUID) -> BytesIO:
        plan = await self.db.get_plan(account_id, plan_id)
        if plan is None:
            raise PlanNotFoundError
        project = await self.db.get_project(account_id, plan.project_id)
        if project is None:
            raise RuntimeError("plan exists but its project does not")
        bytes = export_dxf(project, plan)
        return bytes
