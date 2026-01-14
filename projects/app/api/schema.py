from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

import app.core.plan.models as plan_models
import app.core.project.models as project_models
import app.core.shell.models as shell_models


class Location(BaseModel):
    x: int
    y: int
    z: int


class Line(BaseModel):
    x1: int
    y1: int
    x2: int
    y2: int


class Rect(BaseModel):
    x: int
    y: int
    width: int
    height: int


class Object(BaseModel):
    object_id: UUID


class Door(Object):
    wall_id: UUID
    x: int
    w: int
    h: int


class Window(Object):
    wall_id: UUID
    x: int
    y: int
    w: int
    h: int


class Wall(Object):
    x1: int
    y1: int
    x2: int
    y2: int


class WetArea(Object):
    x: int
    y: int
    w: int
    h: int


class ShellContent(BaseModel):
    version: int = 0
    walls: list[Wall] = []
    doors: list[Door] = []
    windows: list[Window] = []
    wet_areas: list[WetArea] = []


class Shell(BaseModel):
    id: UUID
    name: str = Field(max_length=256)
    content: ShellContent
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def from_core(shell: shell_models.Shell) -> "Shell":
        return Shell(**shell.model_dump())


class PatchShell(BaseModel):
    pass


class PatchPlan(BaseModel):
    name: str


class AddObjectOperation(BaseModel):
    object_id: UUID
    location: Location


class UpdatePlan(BaseModel):
    add_objects: list[AddObjectOperation] = Field(default=[])
    delete_objects: list[UUID] = Field(default=[])
    update_objects: list[UUID] = Field(default=[])


class PatchProject(BaseModel):
    name: str | None = Field(None, max_length=256)
    description: str | None = Field(None, max_length=2048)


class Plan(BaseModel):
    id: UUID
    name: str = Field(max_length=256)
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def from_core(plan: plan_models.Plan) -> "Plan":
        return Plan(**plan.model_dump())


class Project(BaseModel):
    id: UUID
    name: str = Field(max_length=256)
    description: str = Field(max_length=2048)
    pinned: bool
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def from_core(project: project_models.Project) -> "Project":
        return Project(**project.model_dump())
