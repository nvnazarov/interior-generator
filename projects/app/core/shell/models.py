from datetime import datetime, timezone
from typing import Sequence
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ValidationError, model_validator

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


class Patch(BaseModel):
    version: int = 0
    walls: dict[UUID, WallPatch | None] = {}
    doors: dict[UUID, DoorPatch | None] = {}
    windows: dict[UUID, WindowPatch | None] = {}
    wet_areas: dict[UUID, WetAreaPatch | None] = {}


class Content(BaseModel):
    walls: dict[UUID, Wall] = {}
    doors: dict[UUID, Door] = {}
    windows: dict[UUID, Window] = {}
    wet_areas: dict[UUID, WetArea] = {}


class Shell(BaseModel):
    id: UUID
    account_id: UUID
    name: str = Field(max_length=256)
    version: int
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
            version=0,
            content=Content(),
            created_at=dt,
            updated_at=dt,
        )

    def rename(self, name: str):
        self.name = name
        self.updated_at = datetime.now(tz=timezone.utc)

    def patch(self, patch: Patch):
        if patch.version != self.version:
            raise ShellVersionConflictError

        attrs: Sequence[tuple[str, type[BaseModel]]] = [
            ("walls", Wall),
            ("doors", Door),
            ("windows", Window),
            ("wet_areas", WetArea),
        ]
        for attr, cls in attrs:
            # fmt: off
            entities_patches: dict[UUID, BaseModel | None] = patch.__getattribute__(attr)
            for id, entity_patch in entities_patches.items():
                entities: dict[UUID, BaseModel] = self.content.__getattribute__(attr)
                if (entity := entities.get(id)) is None:
                    if entity_patch is None:
                        raise ShellPatchError("deleting non existing entity")
                    try:
                        entities[id] = cls(**entity_patch.model_dump())
                    except ValidationError as e:
                        raise ShellPatchError(f"invalid adding patch: {e}")
                elif entity_patch is None:
                    del entities[id]
                else:
                    model = entity.model_dump()
                    for k, v in entity_patch.model_dump().items():
                        if v is not None:
                            model[k] = v
                    entities[id] = cls(**model)
            # fmt: on

        for id, window in self.content.windows.items():
            wall = self.content.walls.get(window.wall_id)
            if wall is None:
                raise ShellPatchError(
                    f"window[{id}] is attached to non existing wall[{window.wall_id}]"
                )
            if window.x + window.w > wall.length():
                raise ShellPatchError(f"window[{id}] is out of wall[{wall.id}] bounds")

        for id, door in self.content.doors.items():
            wall = self.content.walls.get(door.wall_id)
            if wall is None:
                raise ShellPatchError(
                    f"door[{id}] is attached to non existing wall[{door.wall_id}]"
                )
            if door.x + door.w > wall.length():
                raise ShellPatchError(f"door[{id}] is out of wall[{wall.id}] bounds")

        self.updated_at = datetime.now(tz=timezone.utc)
