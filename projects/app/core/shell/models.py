from datetime import datetime, timezone
from typing import Any, Sequence
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator

from app.core.shell.errors import (
    ShellPatchError,
    ShellsPerAccountLimitExceededError,
    ShellVersionConflictError,
)


class Quota(BaseModel):
    account_id: UUID
    max_shells_count: int = Field(ge=0)
    current_shells_count: int = Field(ge=0)
    version: int

    @staticmethod
    def create(account_id: UUID, max_shells_count: int) -> "Quota":
        return Quota(
            account_id=account_id,
            max_shells_count=max_shells_count,
            current_shells_count=0,
            version=0,
        )

    def increase(self):
        if self.current_shells_count >= self.max_shells_count:
            raise ShellsPerAccountLimitExceededError
        self.current_shells_count += 1

    def decrease(self):
        if self.current_shells_count > 0:
            self.current_shells_count -= 1


class Object(BaseModel):
    object_id: UUID


class Door(Object):
    wall_id: UUID
    x: int = Field(ge=0)
    w: int = Field(ge=0)
    h: int = Field(ge=0)


class Window(Object):
    wall_id: UUID
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    w: int = Field(ge=0)
    h: int = Field(ge=0)


class Wall(Object):
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


class WetArea(Object):
    x: int
    y: int
    w: int = Field(ge=0)
    h: int = Field(ge=0)


class Patch(BaseModel):
    version: int = 0
    walls: list[Wall] = []
    doors: list[Door] = []
    windows: list[Window] = []
    wet_areas: list[WetArea] = []
    delete_objects: list[UUID] = []


class Content(BaseModel):
    version: int = 0
    walls: list[Wall] = []
    doors: list[Door] = []
    windows: list[Window] = []
    wet_areas: list[WetArea] = []


class Shell(BaseModel):
    id: UUID
    account_id: UUID
    name: str = Field(max_length=256)
    content: Content
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def create(account_id: UUID) -> "Shell":
        dt = datetime.now(tz=timezone.utc)
        return Shell(
            id=uuid4(),
            account_id=account_id,
            name="",
            content=Content(),
            created_at=dt,
            updated_at=dt,
        )

    def rename(self, name: str):
        self.name = name
        self.updated_at = datetime.now(tz=timezone.utc)

    def patch(self, patch: Patch):
        if patch.version != self.content.version:
            raise ShellVersionConflictError

        print(patch)

        new_content = Content(version=patch.version)
        new_content.walls = list(
            filter(
                lambda wall: wall.object_id not in patch.delete_objects,
                self.content.walls,
            )
        )
        new_content.doors = list(
            filter(
                lambda door: door.object_id not in patch.delete_objects,
                self.content.doors,
            )
        )
        new_content.windows = list(
            filter(
                lambda window: window.object_id not in patch.delete_objects,
                self.content.windows,
            )
        )
        new_content.wet_areas = list(
            filter(
                lambda wet_area: wet_area.object_id not in patch.delete_objects,
                self.content.wet_areas,
            )
        )
        for wall in patch.walls:
            result = self._one_or_none(new_content.walls, wall.object_id)
            if result is None:
                new_content.walls.append(wall)
            else:
                idx, _ = result
                new_content.walls[idx] = wall
        for door in patch.doors:
            result = self._one_or_none(new_content.doors, door.object_id)
            if result is None:
                new_content.doors.append(door)
            else:
                idx, _ = result
                new_content.doors[idx] = door
        for window in patch.windows:
            result = self._one_or_none(new_content.windows, window.object_id)
            if result is None:
                new_content.windows.append(window)
            else:
                idx, _ = result
                new_content.windows[idx] = window
        for wet_area in patch.wet_areas:
            result = self._one_or_none(new_content.wet_areas, wet_area.object_id)
            if result is None:
                new_content.wet_areas.append(wet_area)
            else:
                idx, _ = result
                new_content.wet_areas[idx] = wet_area

        # Verify that doors and windows are correctly attached to walls.
        for door in new_content.doors:
            wall: Wall = self._get(new_content.walls, door.wall_id)
            print(door, wall)
            if door.x + door.w > wall.length():
                raise ShellPatchError
        for window in new_content.windows:
            wall: Wall = self._get(new_content.walls, window.wall_id)
            print(window, wall)
            if window.x + window.w > wall.length():
                raise ShellPatchError

        self.content = new_content
        self.updated_at = datetime.now(tz=timezone.utc)

    @staticmethod
    def _get(seq: Sequence[Object], object_id: UUID, default: Any = None) -> Any:
        objects = list(filter(lambda obj: obj.object_id == object_id, seq))
        if len(objects) > 1:
            raise ShellPatchError
        if len(objects) == 0:
            if default is None:
                raise ShellPatchError
            return default
        return objects[0]

    @staticmethod
    def _one_or_none(seq: Sequence[Object], object_id: UUID) -> tuple[int, Any] | None:
        seq_with_indices = enumerate(seq)
        objects_with_indices = list(
            filter(lambda x: x[1].object_id == object_id, seq_with_indices)
        )
        if len(objects_with_indices) > 1:
            raise ShellPatchError
        if len(objects_with_indices) == 0:
            return None
        return objects_with_indices[0]
