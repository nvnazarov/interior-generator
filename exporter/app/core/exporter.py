from io import BytesIO

from app.core.catalog import Catalog
from app.core.pdf import PDFRenderer
from app.core.projects import ProjectsService


class ProjectNotFoundError(Exception): ...


class Exporter:
    def __init__(self, projects: ProjectsService, catalog: Catalog):
        self.projects = projects
        self.catalog = catalog

    async def export_project_pdf(self, project_id: str, account_id: str) -> BytesIO:
        project = await self.projects.find_project_by_id(account_id, project_id)
        if project is None:
            raise ProjectNotFoundError
        buffer = BytesIO()
        renderer = PDFRenderer(buffer)
        renderer.draw_project(project)
        async for plan in self.projects.iter_plans_in_project(account_id, project_id):
            await renderer.draw_plan(project, plan, self.catalog)
        renderer.close()
        buffer.seek(0)
        return buffer
