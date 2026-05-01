import pytest

from app.core.account import Account, NoProjectsError, ProjectsLimitExceededError
from app.core.plan import Plan, PlanPatchError, PlanRevisionError
from app.core.project import (
    NoPlansError,
    PlansLimitExceededError,
    Project,
    ProjectPatchError,
    ProjectRevisionError,
)


@pytest.mark.unit
@pytest.mark.parametrize(["limit"], [(0,), (5,), (10,)])
def test_account_projects_limit(limit: int):
    account = Account.create("test", projects_count=0, projects_limit=limit)
    with pytest.raises(NoProjectsError):
        account.delete_project("test")
    projects = list[Project]()
    for _ in range(limit):
        project = account.create_project(plans_limit=5)
        projects.append(project)
    with pytest.raises(ProjectsLimitExceededError):
        account.create_project(plans_limit=5)
    for project in projects:
        account.delete_project(project.id)
    with pytest.raises(NoProjectsError):
        account.delete_project("test")


@pytest.mark.unit
def test_project_ownership():
    account = Account.create("test", projects_count=0, projects_limit=5)
    project = account.create_project(plans_limit=5)

    assert project.is_owned_by("test")
    assert not project.is_owned_by("test-0")

    assert project.can_be_read_by("test")
    assert not project.can_be_read_by("test-0")

    project.publish()
    assert project.published
    assert project.published_at is not None
    assert project.can_be_read_by("test")
    assert project.can_be_read_by("test-0")

    project.unpublish()
    assert not project.published
    assert project.published_at is None
    assert project.can_be_read_by("test")
    assert not project.can_be_read_by("test-0")


@pytest.mark.unit
def test_project_plans_limit():
    account = Account.create("test", projects_count=0, projects_limit=5)
    project = account.create_project(plans_limit=5)

    with pytest.raises(NoPlansError):
        project.delete_plan("test")
    plans = list[Plan]()
    for _ in range(5):
        plan = project.create_plan()
        plans.append(plan)
    with pytest.raises(PlansLimitExceededError):
        project.create_plan()
    for plan in plans:
        project.delete_plan(plan.id)
    with pytest.raises(NoPlansError):
        project.delete_plan("test")


@pytest.mark.unit
def test_project_patching():
    account = Account.create("test", projects_count=0, projects_limit=5)
    project = account.create_project(plans_limit=5)

    assert len(project.content.doors) == 0
    assert len(project.content.windows) == 0
    assert len(project.content.wet_areas) == 0
    assert len(project.content.walls) == 0
    assert project.revision == 0

    with pytest.raises(ProjectRevisionError):
        project.patch(Project.Patch(), 1)
    with pytest.raises(ProjectPatchError):
        project.patch(
            Project.Patch(
                name="test",
                content=Project.Patch.Content(
                    windows={
                        "0": Project.Patch.Content.Window(
                            wall_id="test", x=None, y=None, w=None, h=None
                        )
                    }
                ),
            ),
            0,
        )


@pytest.mark.unit
def test_plan_patching():
    account = Account.create("test", projects_count=0, projects_limit=5)
    project = account.create_project(plans_limit=5)
    plan = project.create_plan()

    assert len(plan.content.areas) == 0
    assert len(plan.content.furniture) == 0
    assert plan.revision == 0

    with pytest.raises(PlanRevisionError):
        plan.patch(Plan.Patch(), 1)
    with pytest.raises(PlanPatchError):
        plan.patch(
            Plan.Patch(
                content=Plan.Patch.Content(
                    furniture={"test": Plan.Patch.Content.Furniture(x=0)}
                )
            ),
            0,
        )
    with pytest.raises(PlanPatchError):
        plan.patch(
            Plan.Patch(
                content=Plan.Patch.Content(
                    areas={"test": Plan.Patch.Content.Area(type="test")}
                )
            ),
            0,
        )

    Point = Plan.Patch.Content.Area.Point

    plan.patch(
        Plan.Patch(
            content=Plan.Patch.Content(
                furniture={
                    "test": Plan.Patch.Content.Furniture(
                        furniture_id="test", x=1, y=2, z=3, yaw=90
                    )
                },
                areas={
                    "test": Plan.Patch.Content.Area(
                        type="test", points=[Point(x=0, y=0)]
                    )
                },
            )
        ),
        0,
    )
    assert plan.revision == 1
    assert plan.content.model_dump() == {
        "furniture": {
            "test": {
                "furniture_id": "test",
                "x": 1,
                "y": 2,
                "z": 3,
                "yaw": 90,
            },
        },
        "areas": {
            "test": {
                "type": "test",
                "points": [
                    {"x": 0, "y": 0},
                ],
            },
        },
    }

    plan.patch(
        Plan.Patch(
            content=Plan.Patch.Content(
                furniture={"test": Plan.Patch.Content.Furniture(x=5)},
                areas={"test": Plan.Patch.Content.Area(type="test-1")},
            )
        ),
        1,
    )
    assert plan.content.model_dump() == {
        "furniture": {
            "test": {
                "furniture_id": "test",
                "x": 5,
                "y": 2,
                "z": 3,
                "yaw": 90,
            },
        },
        "areas": {
            "test": {
                "type": "test-1",
                "points": [
                    {"x": 0, "y": 0},
                ],
            },
        },
    }

    plan.patch(
        Plan.Patch(
            content=Plan.Patch.Content(
                furniture={"test": None},
                areas={"test": None},
            )
        ),
        2,
    )
    assert len(plan.content.areas) == 0
    assert len(plan.content.furniture) == 0
