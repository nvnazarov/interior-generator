from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.core.shell import models


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


class Content(BaseModel):
    version: int = 0
    walls: list[Wall] = []
    doors: list[Door] = []
    windows: list[Window] = []
    wet_areas: list[WetArea] = []


class Shell(BaseModel):
    id: UUID
    name: str = Field(max_length=256)
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
    walls: list[Wall] = []
    doors: list[Door] = []
    windows: list[Window] = []
    wet_areas: list[WetArea] = []
    delete_objects: list[UUID] = []

    def to_model(self) -> models.Patch:
        return models.Patch(**self.model_dump())
