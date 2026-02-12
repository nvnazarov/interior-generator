from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.core.project import Patch as CorePatch
from app.core.project import Project as CoreProject


class Door(BaseModel):
    id: UUID
    wall_id: UUID
    x: int = Field(ge=0)
    w: int = Field(ge=0)
    h: int = Field(ge=0)


class DoorPatch(BaseModel):
    id: UUID | None = None
    wall_id: UUID | None = None
    x: int | None = Field(None, ge=0)
    w: int | None = Field(None, ge=0)
    h: int | None = Field(None, ge=0)


class Window(BaseModel):
    id: UUID
    wall_id: UUID
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    w: int = Field(ge=0)
    h: int = Field(ge=0)


class WindowPatch(BaseModel):
    id: UUID | None = None
    wall_id: UUID | None = None
    x: int | None = Field(None, ge=0)
    y: int | None = Field(None, ge=0)
    w: int | None = Field(None, ge=0)
    h: int | None = Field(None, ge=0)


class Wall(BaseModel):
    id: UUID
    x1: int
    y1: int
    x2: int
    y2: int

    @model_validator(mode="after")
    def validate_wall_is_parallel_to_axes(self) -> "Wall":
        if self.x1 != self.x2 and self.y1 != self.y2:
            raise ValueError("wall is not parallel to axes")
        return self

    def length(self):
        return abs(self.x1 - self.x2) + abs(self.y1 - self.y2)


class WallPatch(BaseModel):
    id: UUID | None = None
    x1: int | None = None
    y1: int | None = None
    x2: int | None = None
    y2: int | None = None


class WetArea(BaseModel):
    id: UUID
    x: int
    y: int
    w: int = Field(ge=0)
    h: int = Field(ge=0)


class WetAreaPatch(BaseModel):
    id: UUID | None = None
    x: int | None = None
    y: int | None = None
    w: int | None = Field(None, ge=0)
    h: int | None = Field(None, ge=0)


class Content(BaseModel):
    walls: dict[UUID, Wall] = {}
    doors: dict[UUID, Door] = {}
    windows: dict[UUID, Window] = {}
    wet_areas: dict[UUID, WetArea] = {}


class ContentPatch(BaseModel):
    walls: dict[UUID, WallPatch | None] = {}
    doors: dict[UUID, DoorPatch | None] = {}
    windows: dict[UUID, WindowPatch | None] = {}
    wet_areas: dict[UUID, WetAreaPatch | None] = {}


class Patch(BaseModel):
    name: str | None = Field(None, max_length=256)
    description: str | None = Field(None, max_length=2048)
    content: ContentPatch | None = None

    def to_core(self):
        return CorePatch(**self.model_dump())


class Project(BaseModel):
    id: UUID
    name: str = Field(max_length=256)
    description: str = Field(max_length=2048)
    content: Content | None = None
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def from_core(project: CoreProject) -> "Project":
        return Project(**project.model_dump())
