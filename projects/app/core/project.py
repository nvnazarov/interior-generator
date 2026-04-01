import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Sequence
from uuid import UUID

from pydantic import BaseModel, Field, ValidationError

from app.core.plan import Plan
from app.core.util import now

logger = logging.getLogger(__name__)


class RevisionError(Exception): ...


class PatchError(Exception): ...


class PlansLimitExceededError(Exception): ...


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


class WetArea(BaseModel):
    id: str
    x: int
    y: int
    w: int = Field(ge=0)
    h: int = Field(ge=0)


class WetAreaPatch(BaseModel):
    id: str | None = None
    x: int | None = None
    y: int | None = None
    w: int | None = Field(None, ge=0)
    h: int | None = Field(None, ge=0)


class ContentPatch(BaseModel):
    walls: dict[str, WallPatch | None] = {}
    doors: dict[str, DoorPatch | None] = {}
    windows: dict[str, WindowPatch | None] = {}
    wet_areas: dict[str, WetAreaPatch | None] = {}


class Patch(BaseModel):
    name: str | None = None
    description: str | None = None
    content: ContentPatch | None = None


class Content(BaseModel):
    walls: dict[str, Wall] = {}
    doors: dict[str, Door] = {}
    windows: dict[str, Window] = {}
    wet_areas: dict[str, WetArea] = {}


class Project(BaseModel):
    id: UUID
    account_id: str
    name: str = Field(max_length=256)
    description: str = Field(max_length=2048)
    revision: int = 0
    published: bool = False
    content: Content = Field(default_factory=lambda: Content())
    created_at: datetime = Field(default_factory=now)
    updated_at: datetime = Field(default_factory=now)
    plans_count: int = 0
    plans_limit: int = 0

    def create_plan(self, *, name: str = "") -> Plan:
        if self.plans_count >= self.plans_limit:
            raise PlansLimitExceededError
        self.plans_count += 1
        return Plan.empty(self.id, name=name)

    def delete_plan(self, plan_id: UUID):
        self.plans_count = max(0, self.plans_count - 1)

    def publish(self):
        self.published = True
        self.updated_at = now()

    def unpublish(self):
        self.published = False
        self.updated_at = now()

    def is_owned_by(self, account_id: str):
        return self.account_id == account_id

    def can_be_read_by(self, account_id: str):
        return self.account_id == account_id or self.published

    def patch(self, patch: Patch, revision: int):
        if revision != self.revision:
            raise RevisionError

        if patch.name is not None:
            self.name = patch.name
        if patch.description is not None:
            self.description = patch.description
        if patch.content is not None:
            attrs: Sequence[tuple[str, type[BaseModel]]] = [
                ("walls", Wall),
                ("doors", Door),
                ("windows", Window),
                ("wet_areas", WetArea),
            ]
            for attr, cls in attrs:
                # fmt: off
                entities_patches: dict[str, BaseModel | None] = patch.content.__getattribute__(attr)
                for id, entity_patch in entities_patches.items():
                    entities: dict[str, BaseModel] = self.content.__getattribute__(attr)
                    if (entity := entities.get(id)) is None:
                        if entity_patch is None:
                            continue
                            # msg = "deleting non existing entity"
                            # logger.error({"msg": msg})
                            # raise PatchError("deleting non existing entity")
                        try:
                            entities[id] = cls(**entity_patch.model_dump())
                        except ValidationError as e:
                            msg = f"invalid adding patch: {e}"
                            logger.error({"msg": msg})
                            raise PatchError(msg)
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
                    msg = f"window[{id}] is attached to non existing wall[{window.wall_id}]"
                    logger.error({"msg": msg})
                    raise PatchError(msg)
                if window.x + window.w > wall.length():
                    msg = f"window[{id}] is out of wall[{wall.id}] bounds"
                    logger.error({"msg": msg})
                    raise PatchError(msg)

            for id, door in self.content.doors.items():
                wall = self.content.walls.get(door.wall_id)
                if wall is None:
                    msg = f"door[{id}] is attached to non existing wall[{door.wall_id}]"
                    logger.error({"msg": msg})
                    raise PatchError(msg)
                if door.x + door.w > wall.length():
                    msg = f"door[{id}] is out of wall[{wall.id}] bounds"
                    logger.error({"msg": msg})
                    raise PatchError(f"door[{id}] is out of wall[{wall.id}] bounds")

        self.revision += 1
        self.updated_at = now()


class ProjectRepository(ABC):
    @abstractmethod
    async def get(self, project_id: UUID) -> Project | None: ...

    @abstractmethod
    async def save(self, project: Project) -> None: ...

    @abstractmethod
    async def get_without_content(self, project_id: UUID) -> Project | None: ...

    @abstractmethod
    async def save_without_content(self, project: Project) -> None: ...

    @abstractmethod
    async def delete(self, project_id: UUID) -> None: ...

    @abstractmethod
    async def get_all_owned_by_account(self, account_id: str) -> list[Project]: ...
