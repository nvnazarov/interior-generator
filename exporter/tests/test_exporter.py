from unittest.mock import Mock

import pypdf
import pytest
from hypothesis import given
from hypothesis import strategies as st

from app.core.catalog import Catalog
from app.core.exporter import Exporter, ProjectNotFoundError
from app.core.models import Furniture, Plan, Project
from app.core.projects import ProjectsService


@st.composite
def wall(draw: st.DrawFn):
    [x1, y1, x2, y2] = draw(st.lists(st.integers(), min_size=4, max_size=4))
    return Project.Content.Wall(x1=x1, y1=y1, x2=x2, y2=y2)


@st.composite
def window(draw: st.DrawFn, walls: list[str]):
    [x, y, w, h] = draw(st.lists(st.integers(min_value=0), min_size=4, max_size=4))
    wall_id = draw(st.sampled_from(walls)) if walls else ""
    return Project.Content.Window(wall_id=wall_id, x=x, y=y, w=w, h=h)


@st.composite
def door(draw: st.DrawFn, walls: list[str]):
    [x, w, h] = draw(st.lists(st.integers(min_value=0), min_size=3, max_size=3))
    wall_id = draw(st.sampled_from(walls)) if walls else ""
    return Project.Content.Door(wall_id=wall_id, x=x, w=w, h=h)


@st.composite
def wet_area(draw: st.DrawFn):
    points = draw(
        st.lists(st.tuples(st.integers(), st.integers()), min_size=3, max_size=10)
    )
    return Project.Content.WetArea(
        points=[
            Project.Content.WetArea.Point(x=point[0], y=point[1]) for point in points
        ]
    )


@st.composite
def furniture(draw: st.DrawFn):
    [x, y, z] = draw(st.lists(st.integers(), min_size=3, max_size=3))
    yaw = draw(st.floats(allow_infinity=False, allow_nan=False))
    furniture_id = draw(st.characters())
    return Plan.Content.Furniture(furniture_id=furniture_id, x=x, y=y, z=z, yaw=yaw)


@st.composite
def area(draw: st.DrawFn):
    points = draw(
        st.lists(st.tuples(st.integers(), st.integers()), min_size=3, max_size=10)
    )
    type = draw(
        st.sampled_from(["kitchen", "bathroom", "bedroom", "hallway", "livingroom"])
        | st.characters()
    )
    return Plan.Content.Area(
        type=type,
        points=[Plan.Content.Area.Point(x=point[0], y=point[1]) for point in points],
    )


@st.composite
def plan_content(draw: st.DrawFn):
    areas = draw(st.dictionaries(st.characters(), area(), max_size=5))
    furniture_ = draw(st.dictionaries(st.characters(), furniture(), max_size=5))
    return Plan.Content(areas=areas, furniture=furniture_)


@st.composite
def project_content(draw: st.DrawFn):
    walls = draw(st.dictionaries(st.characters(), wall(), max_size=5))
    walls_ids = [id for id in walls.keys()]
    doors = draw(st.dictionaries(st.characters(), door(walls_ids), max_size=5))
    windows = draw(st.dictionaries(st.characters(), window(walls_ids), max_size=5))
    wet_areas = draw(st.dictionaries(st.characters(), wet_area(), max_size=5))
    return Project.Content(
        walls=walls, doors=doors, windows=windows, wet_areas=wet_areas
    )


@pytest.mark.asyncio
@given(
    project_content=project_content(),
    plans_contents=st.lists(plan_content(), min_size=1, max_size=5),
)
async def test_export_project_pdf(
    project_content: Project.Content,
    plans_contents: list[Plan.Content],
):
    class FakeCatalog(Catalog):
        def __init__(self):
            self.calls_count = 0

        async def find_furniture_by_id(self, id: str) -> Furniture | None:
            if self.calls_count % 3 == 0:
                return None
            return Furniture(id=id, name="test", width=20, height=20, depth=20)

    catalog = FakeCatalog()
    projects = Mock(ProjectsService)
    exporter = Exporter(projects, catalog)
    project = Project(
        id="test-project",
        account_id="test-account",
        name="test",
        content=project_content,
    )
    projects.find_project_by_id.return_value = project

    async def iter_plans():
        for i, content in enumerate(plans_contents):
            yield Plan(
                id=f"test-plan-{i}",
                project_id=project.id,
                name=f"test-plan-{i}",
                content=content,
            )

    projects.iter_plans_in_project.return_value = iter_plans()

    bytes = await exporter.export_project_pdf(project.id, project.account_id)

    projects.find_project_by_id.assert_called_once_with(project.account_id, project.id)
    projects.iter_plans_in_project.assert_called_once_with(
        project.account_id, project.id
    )

    reader = pypdf.PdfReader(bytes)
    assert reader.get_num_pages() == 1 + len(plans_contents)


@pytest.mark.asyncio
async def test_export_absent_project_pdf(exporter: Exporter, projects: Mock):
    projects.find_project_by_id.return_value = None

    with pytest.raises(ProjectNotFoundError):
        _ = await exporter.export_project_pdf("test-project", "test-account")

    projects.find_project_by_id.assert_called_once_with("test-account", "test-project")
    projects.iter_plans_in_project.assert_not_called()
