from unittest.mock import Mock

import pypdf
import pytest

from app.core.exporter import Exporter, ProjectNotFoundError
from app.core.models import Plan, Project


@pytest.mark.asyncio
async def test_export_project_pdf(exporter: Exporter, projects: Mock):
    project = Project(id="test-project", account_id="test-account", name="test")
    projects.find_project_by_id.return_value = project

    async def iter_plans():
        yield Plan(id="test-plan", project_id=project.id, name="test")

    projects.iter_plans_in_project.return_value = iter_plans()

    bytes = await exporter.export_project_pdf(project.id, project.account_id)

    projects.find_project_by_id.assert_called_once_with(project.account_id, project.id)
    projects.iter_plans_in_project.assert_called_once_with(
        project.account_id, project.id
    )

    reader = pypdf.PdfReader(bytes)
    assert reader.get_num_pages() == 2


@pytest.mark.asyncio
async def test_export_absent_project_pdf(exporter: Exporter, projects: Mock):
    projects.find_project_by_id.return_value = None

    with pytest.raises(ProjectNotFoundError):
        _ = await exporter.export_project_pdf("test-project", "test-account")

    projects.find_project_by_id.assert_called_once_with("test-account", "test-project")
    projects.iter_plans_in_project.assert_not_called()
