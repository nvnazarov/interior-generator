from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.core.project import Patch as CorePatch
from app.core.project import Project as CoreProject


class Door(BaseModel):
    id: str
    wall_id: str
    x: int = Field(ge=0)
    w: int = Field(ge=0)
    h: int = Field(ge=0)


class DoorPatch(BaseModel):
    id: str | None = None
    wall_id: str | None = None
    x: int | None = Field(None, ge=0)
    w: int | None = Field(None, ge=0)
    h: int | None = Field(None, ge=0)


class Window(BaseModel):
    id: str
    wall_id: str
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    w: int = Field(ge=0)
    h: int = Field(ge=0)


class WindowPatch(BaseModel):
    id: str | None = None
    wall_id: str | None = None
    x: int | None = Field(None, ge=0)
    y: int | None = Field(None, ge=0)
    w: int | None = Field(None, ge=0)
    h: int | None = Field(None, ge=0)


class Wall(BaseModel):
    id: str
    x1: int
    y1: int
    x2: int
    y2: int

    def length(self):
        return abs(self.x1 - self.x2) + abs(self.y1 - self.y2)


class WallPatch(BaseModel):
    id: str | None = None
    x1: int | None = None
    y1: int | None = None
    x2: int | None = None
    y2: int | None = None


class Point(BaseModel):
    x: int
    y: int


class WetArea(BaseModel):
    id: str
    points: list[Point]


class WetAreaPatch(BaseModel):
    id: str | None = None
    points: list[Point] | None = None


class Content(BaseModel):
    walls: dict[str, Wall] = {}
    doors: dict[str, Door] = {}
    windows: dict[str, Window] = {}
    wet_areas: dict[str, WetArea] = {}


class ContentPatch(BaseModel):
    walls: dict[str, WallPatch | None] = {}
    doors: dict[str, DoorPatch | None] = {}
    windows: dict[str, WindowPatch | None] = {}
    wet_areas: dict[str, WetAreaPatch | None] = {}


class Patch(BaseModel):
    name: str | None = Field(None, max_length=256)
    description: str | None = Field(None, max_length=2048)
    content: ContentPatch | None = None

    def to_core(self):
        return CorePatch(**self.model_dump())


class Project(BaseModel):
    id: UUID
    account_id: str
    name: str = Field(max_length=256)
    description: str = Field(max_length=2048)
    content: Content | None = None
    published: bool = False
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def from_core(project: CoreProject) -> "Project":
        return Project(**project.model_dump())
