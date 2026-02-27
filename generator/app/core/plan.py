from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ValidationError

from app.core.timeutil import current_time


class RevisionError(Exception): ...


class PatchError(Exception): ...


class Furniture(BaseModel):
    id: UUID
    furniture_id: UUID
    x: int
    y: int
    z: int
    yaw: int


class FurniturePatch(BaseModel):
    id: UUID
    x: int | None = None
    y: int | None = None
    z: int | None = None
    yaw: int | None = None


class Area(BaseModel):
    id: UUID
    type: str
    x: int
    y: int
    w: int
    h: int


class AreaPatch(BaseModel):
    id: UUID
    type: str | None = None
    x: int | None = None
    y: int | None = None
    w: int | None = None
    h: int | None = None


class ContentPatch(BaseModel):
    furniture: dict[UUID, FurniturePatch | None] = {}
    areas: dict[UUID, AreaPatch | None] = {}


class Patch(BaseModel):
    name: str | None = None
    content: ContentPatch | None = None


class Content(BaseModel):
    furniture: dict[UUID, Furniture] = {}
    areas: dict[UUID, Area] = {}


class Plan(BaseModel):
    id: UUID
    project_id: UUID
    revision: int = 0
    content: Content = Field(default_factory=lambda: Content())
    name: str = Field("", max_length=256)
    created_at: datetime = Field(default_factory=current_time)
    updated_at: datetime = Field(default_factory=current_time)

    @staticmethod
    def empty(project_id: UUID, *, name: str = "") -> "Plan":
        dt = current_time()
        return Plan(
            id=uuid4(),
            project_id=project_id,
            revision=0,
            name=name,
            created_at=dt,
            updated_at=dt,
        )

    def patch(self, patch: Patch, revision: int) -> None:
        if revision != self.revision:
            raise RevisionError

        if patch.name is not None:
            self.name = patch.name
        if patch.content is not None:
            for furniture_id, furniture in patch.content.furniture.items():
                if furniture is None:
                    try:
                        self.content.furniture.pop(furniture_id)
                    except KeyError:
                        raise PatchError(
                            f"furniture[id={furniture_id.hex}] does not exist"
                        )
                elif (
                    old_furniture := self.content.furniture.get(furniture_id)
                ) is None:
                    try:
                        self.content.furniture[furniture_id] = Furniture(
                            **furniture.model_dump()
                        )
                    except ValidationError:
                        raise PatchError(
                            f"furniture[id={furniture_id.hex}] must be full"
                        )
                else:
                    self.content.furniture[furniture_id] = self._merge(
                        old_furniture, furniture
                    )

            for area_id, area in patch.content.areas.items():
                if area is None:
                    try:
                        self.content.areas.pop(area_id)
                    except KeyError:
                        raise PatchError(f"area[id={area_id.hex}] does not exist")
                elif (old_area := self.content.areas.get(area_id)) is None:
                    try:
                        self.content.areas[area_id] = Area(**area.model_dump())
                    except ValidationError:
                        raise PatchError(f"area[id={area_id.hex}] must be full")
                else:
                    self.content.areas[area_id] = self._merge(old_area, area)

        self.revision += 1
        self.updated_at = current_time()

    @staticmethod
    def _merge(a: BaseModel, b: BaseModel) -> Any:
        for k, v in b.model_dump().items():
            if v is not None:
                a.__setattr__(k, v)
        return a


class PlanRepository(ABC):
    @abstractmethod
    async def get(self, account_id: UUID, plan_id: UUID) -> Plan | None: ...

    @abstractmethod
    async def save(self, account_id: UUID, plan: Plan) -> None: ...

    @abstractmethod
    async def get_without_content(self, plan_id: UUID) -> Plan | None: ...

    @abstractmethod
    async def save_without_content(self, plan: Plan) -> None: ...

    @abstractmethod
    async def delete(self, plan: Plan) -> None: ...

    @abstractmethod
    async def get_all_of_project(self, project_id: UUID) -> list[Plan]: ...
