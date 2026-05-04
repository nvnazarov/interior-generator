from io import BytesIO
from unittest.mock import Mock

import pypdf
import pytest
from httpx import AsyncClient

from app.core.models import Plan, Project


@pytest.mark.asyncio
async def test_export_project_pdf(client: AsyncClient, projects: Mock):
    project = Project(id="test-project", account_id="test-account", name="test")
    projects.find_project_by_id.return_value = project

    async def iter_plans():
        yield Plan(id="test-plan", project_id=project.id, name="test")

    projects.iter_plans_in_project.return_value = iter_plans()

    resp = await client.post(
        f"/projects/{project.id}/export/pdf", headers={"x-account-id": "test-account"}
    )

    projects.find_project_by_id.assert_called_once_with("test-account", project.id)

    assert resp.status_code == 200
    assert resp.headers.get("content-type") == "application/pdf"
    assert (
        resp.headers.get("content-Disposition")
        == f"attachment; filename=project-{project.id}.pdf"
    )

    reader = pypdf.PdfReader(BytesIO(resp.content))
    assert reader.get_num_pages() == 2


@pytest.mark.asyncio
async def test_export_absent_project_pdf(client: AsyncClient, projects: Mock):
    projects.find_project_by_id.return_value = None
    resp = await client.post(
        "/projects/test-project/export/pdf", headers={"x-account-id": "test-account"}
    )
    assert resp.status_code == 404
    assert resp.json() == {"detail": "project not found"}


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 204
    assert resp.text == ""
