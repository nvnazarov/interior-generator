from datetime import datetime
from uuid import UUID

from pydantic import Field, BaseModel

import projects.core.models as models


class Location(BaseModel):
    x: int
    y: int
    z: int


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


class Project(BaseModel):
    id: UUID
    name: str = Field(max_length=256)
    description: str = Field(max_length=2048)
    pinned: bool
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def from_core(project: models.Project) -> "Project":
        return Project(**project.__dict__)
