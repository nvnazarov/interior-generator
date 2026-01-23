from pathlib import Path
from typing import Any, AsyncGenerator
from unittest.mock import Mock
from uuid import UUID, uuid4

import pytest

from app.core.exporter import Exporter, IProjectsRepository
from app.core.models import Area, AreaType, Plan, Wall


@pytest.mark.asyncio
async def test_exporter():
    async def get_plans(
        project_id: UUID, account_id: UUID
    ) -> AsyncGenerator[Plan, Any]:
        yield Plan(
            name="ВАРИАНТ 1",
            areas=[
                Area(type=AreaType.KITCHEN, x=0, y=0, w=10, h=10),
                Area(type=AreaType.LIVINGROOM, x=0, y=10, w=10, h=10),
                Area(type=AreaType.BATHROOM, x=10, y=10, w=10, h=10),
                Area(type=AreaType.BEDROOM, x=20, y=0, w=10, h=10),
                Area(type=AreaType.WET_AREA, x=10, y=0, w=10, h=10),
            ],
            walls={
                UUID("d1a7a40b-78e4-4ebf-9ef2-f1e779a06351"): Wall(
                    x1=0, x2=0, y1=10, y2=0
                ),
                UUID("d1a7a40b-78e4-4ebf-9ef2-f1e779a06352"): Wall(
                    x1=0,
                    x2=10,
                    y1=0,
                    y2=0,
                ),
            },
        )
        yield Plan(name="ВАРИАНТ 2")

    repository = Mock(IProjectsRepository)
    repository.get_plans = get_plans
    exporter = Exporter(repository)
    bytes = await exporter.export_pdf(uuid4(), uuid4())
    path = Path(__file__).parent / "test.pdf"
    with open(path, "wb") as f:
        f.write(bytes.getbuffer())
