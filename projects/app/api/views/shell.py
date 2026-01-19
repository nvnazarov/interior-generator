from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.core.shell import models


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


class Shell(BaseModel):
    id: UUID
    name: str = Field(max_length=256)
    version: int
    content: Content
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def from_model(shell: models.Shell) -> "Shell":
        return Shell(**shell.model_dump())


class ShellNoContent(BaseModel):
    id: UUID
    name: str = Field(max_length=256)
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def from_model(shell: models.Shell) -> "ShellNoContent":
        return ShellNoContent(**shell.model_dump())


class Patch(BaseModel):
    version: int = 0
    walls: dict[UUID, WallPatch | None] = {}
    doors: dict[UUID, DoorPatch | None] = {}
    windows: dict[UUID, WindowPatch | None] = {}
    wet_areas: dict[UUID, WetAreaPatch | None] = {}

    def to_model(self) -> models.Patch:
        return models.Patch(**self.model_dump())
