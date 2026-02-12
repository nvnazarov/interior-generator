from pathlib import Path
from typing import AsyncIterable
from unittest.mock import Mock
from uuid import UUID, uuid4

import pytest

from app.core.exporter import Exporter, Repository
from app.core.models import Plan, PlanContent, Project, ProjectContent


@pytest.mark.asyncio
async def test_exporter():
    async def get_plans(project_id: UUID, account_id: UUID) -> AsyncIterable[Plan]:
        yield Plan(
            id=uuid4(),
            project_id=project_id,
            name="ВАРИАНТ 1",
            content=PlanContent(),
        )

    repository = Mock(Repository)
    repository.get_project.return_value = Project(
        id=uuid4(),
        name="",
        content=ProjectContent(),
    )
    repository.get_plans_of_project = get_plans
    exporter = Exporter(repository)
    bytes = await exporter.export_project_pdf(uuid4(), uuid4())
    path = Path(__file__).parent / "test.pdf"
    with open(path, "wb") as f:
        f.write(bytes.getbuffer())
