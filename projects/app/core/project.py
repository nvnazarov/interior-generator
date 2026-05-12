import logging
from abc import ABC, abstractmethod
from datetime import datetime
from math import sqrt
from typing import Sequence

from pydantic import BaseModel, Field, ValidationError

from app.core.plan import Plan
from app.core.util import now

logger = logging.getLogger(__name__)


class ProjectRevisionError(Exception): ...


class ProjectPatchError(Exception): ...


class PlansLimitExceededError(Exception): ...


class NoPlansError(Exception): ...


class Project(BaseModel):
    class Patch(BaseModel):
        class Content(BaseModel):
            class Door(BaseModel):
                wall_id: str | None = None
                x: int | None = Field(None, ge=0)
                w: int | None = Field(None, ge=0)
                h: int | None = Field(None, ge=0)

            class Window(BaseModel):
                wall_id: str | None = None
                x: int | None = Field(None, ge=0)
                y: int | None = Field(None, ge=0)
                w: int | None = Field(None, ge=0)
                h: int | None = Field(None, ge=0)

            class Wall(BaseModel):
                x1: int | None = None
                y1: int | None = None
                x2: int | None = None
                y2: int | None = None

            class WetArea(BaseModel):
                class Point(BaseModel):
                    x: int
                    y: int

                points: list[Point] | None = None

            walls: dict[str, Wall | None] = Field(default_factory=dict)
            doors: dict[str, Door | None] = Field(default_factory=dict)
            windows: dict[str, Window | None] = Field(default_factory=dict)
            wet_areas: dict[str, WetArea | None] = Field(default_factory=dict)

        name: str | None = None
        content: Content | None = None

    class Content(BaseModel):
        class Door(BaseModel):
            wall_id: str
            x: int = Field(ge=0)
            w: int = Field(ge=0)
            h: int = Field(ge=0)

        class Window(BaseModel):
            wall_id: str
            x: int = Field(ge=0)
            y: int = Field(ge=0)
            w: int = Field(ge=0)
            h: int = Field(ge=0)

        class Wall(BaseModel):
            x1: int
            y1: int
            x2: int
            y2: int

            def length(self) -> float:
                return sqrt((self.x1 - self.x2) ** 2 + (self.y1 - self.y2) ** 2)

        class WetArea(BaseModel):
            class Point(BaseModel):
                x: int
                y: int

            points: list[Point]

        walls: dict[str, Wall] = Field(default_factory=dict)
        doors: dict[str, Door] = Field(default_factory=dict)
        windows: dict[str, Window] = Field(default_factory=dict)
        wet_areas: dict[str, WetArea] = Field(default_factory=dict)

    id: str
    account_id: str
    name: str = Field(max_length=256)
    revision: int = 0
    published: bool = False
    published_at: datetime | None = None
    content: Content = Field(default_factory=Content)
    created_at: datetime = Field(default_factory=now)
    updated_at: datetime = Field(default_factory=now)
    plans_count: int = 0
    plans_limit: int = 0

    def __hash__(self):
        return hash(
            (self.id, self.revision, self.published, self.plans_count, self.plans_limit)
        )

    def create_plan(self) -> Plan:
        if self.plans_count >= self.plans_limit:
            raise PlansLimitExceededError
        self.plans_count += 1
        return Plan.empty(self.id)

    def delete_plan(self, plan_id: str):
        if self.plans_count == 0:
            raise NoPlansError
        self.plans_count = max(0, self.plans_count - 1)

    def publish(self):
        self.published = True
        self.published_at = now()

    def unpublish(self):
        self.published = False
        self.published_at = None

    def is_owned_by(self, account_id: str):
        return self.account_id == account_id

    def can_be_read_by(self, account_id: str):
        return self.account_id == account_id or self.published

    def patch(self, patch: Patch, revision: int):
        if revision != self.revision:
            raise ProjectRevisionError

        if patch.name is not None:
            self.name = patch.name
        if patch.content is not None:
            attrs: Sequence[tuple[str, type[BaseModel]]] = [
                ("walls", Project.Content.Wall),
                ("doors", Project.Content.Door),
                ("windows", Project.Content.Window),
                ("wet_areas", Project.Content.WetArea),
            ]
            for attr, cls in attrs:
                # fmt: off
                entities_patches: dict[str, BaseModel | None] = patch.content.__getattribute__(attr)
                for id, entity_patch in entities_patches.items():
                    entities: dict[str, BaseModel] = self.content.__getattribute__(attr)
                    if (entity := entities.get(id)) is None:
                        if entity_patch is None:
                            continue
                        try:
                            entities[id] = cls(**entity_patch.model_dump())
                        except ValidationError as e:
                            msg = f"invalid adding patch: {e}"
                            logger.error({"msg": msg})
                            raise ProjectPatchError(msg)
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
                    raise ProjectPatchError(msg)
                if window.x + window.w > wall.length():
                    msg = f"window[{id}] is out of wall[{window.wall_id}] bounds"
                    logger.error({"msg": msg})
                    raise ProjectPatchError(msg)

            for id, door in self.content.doors.items():
                wall = self.content.walls.get(door.wall_id)
                if wall is None:
                    msg = f"door[{id}] is attached to non existing wall[{door.wall_id}]"
                    logger.error({"msg": msg})
                    raise ProjectPatchError(msg)
                if door.x + door.w > wall.length():
                    msg = f"door[{id}] is out of wall[{door.wall_id}] bounds"
                    logger.error({"msg": msg})
                    raise ProjectPatchError(
                        f"door[{id}] is out of wall[{door.wall_id}] bounds"
                    )

        self.revision += 1
        self.updated_at = now()


class ProjectsRepository(ABC):
    @abstractmethod
    async def find(self, project_id: str) -> Project | None: ...

    @abstractmethod
    async def save(self, project: Project) -> None: ...

    @abstractmethod
    async def find_without_content(self, project_id: str) -> Project | None: ...

    @abstractmethod
    async def save_without_content(self, project: Project) -> None: ...

    @abstractmethod
    async def delete(self, project_id: str) -> None: ...

    @abstractmethod
    async def owned_by_account(self, account_id: str) -> list[Project]: ...
