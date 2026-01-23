from abc import ABC, abstractmethod
from io import BytesIO
from typing import AsyncIterable
from uuid import UUID

from app.core.models import Plan
from app.core.pdf import PDFRenderer


class IProjectsRepository(ABC):
    @abstractmethod
    def get_plans(self, project_id: UUID, account_id: UUID) -> AsyncIterable[Plan]: ...


class Exporter:
    def __init__(self, projects: IProjectsRepository):
        self.projects = projects

    async def export_pdf(self, project_id: UUID, account_id: UUID) -> BytesIO:
        buffer = BytesIO()
        renderer = PDFRenderer(buffer)
        async for plan in self.projects.get_plans(project_id, account_id):
            renderer.draw_plan(plan)
        renderer.close()
        buffer.seek(0)
        return buffer

    async def export_dxf(self, project_id: UUID, account_id: UUID) -> BytesIO:
        buffer = BytesIO()
        # TODO: export logic
        buffer.seek(0)
        return buffer
