from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ValidationError

from app.core.plan.errors import (
    PlanPatchError,
    PlansPerProjectLimitExceededError,
    PlanVersionConflictError,
)


class Quota(BaseModel):
    project_id: UUID
    max_plans_count: int = Field(ge=0)
    current_plans_count: int = Field(ge=0)
    version: int

    @staticmethod
    def create(project_id: UUID, max_plans_count: int) -> "Quota":
        return Quota(
            project_id=project_id,
            max_plans_count=max_plans_count,
            current_plans_count=0,
            version=0,
        )

    def increase(self):
        if self.current_plans_count >= self.max_plans_count:
            raise PlansPerProjectLimitExceededError
        self.current_plans_count += 1

    def decrease(self):
        if self.current_plans_count > 0:
            self.current_plans_count -= 1


class Furniture(BaseModel):
    id: UUID
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


class Patch(BaseModel):
    version: int = 0
    furniture: dict[UUID, FurniturePatch | None] = {}
    areas: dict[UUID, AreaPatch | None] = {}


class Content(BaseModel):
    furniture: dict[UUID, Furniture] = {}
    areas: dict[UUID, Area] = {}


class Plan(BaseModel):
    id: UUID
    project_id: UUID
    shell_id: UUID
    version: int = 0
    content: Content
    name: str = Field(max_length=256)
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def create(project_id: UUID, shell_id: UUID) -> "Plan":
        return Plan(
            id=uuid4(),
            project_id=project_id,
            shell_id=shell_id,
            name="",
            content=Content(),
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )

    def rename(self, name: str):
        self.name = name
        self.updated_at = datetime.now(tz=timezone.utc)

    def patch(self, patch: Patch):
        if patch.version != self.version:
            raise PlanVersionConflictError

        for furniture_id, furniture in patch.furniture.items():
            if furniture is None:
                try:
                    self.content.furniture.pop(furniture_id)
                except KeyError:
                    raise PlanPatchError(
                        f"furniture[id={furniture_id.hex}] does not exist"
                    )
            elif (old_furniture := self.content.furniture.get(furniture_id)) is None:
                try:
                    self.content.furniture[furniture_id] = Furniture(
                        **furniture.model_dump()
                    )
                except ValidationError:
                    raise PlanPatchError(
                        f"furniture[id={furniture_id.hex}] must be full"
                    )
            else:
                self.content.furniture[furniture_id] = self._merge(
                    old_furniture, furniture
                )

        for area_id, area in patch.areas.items():
            if area is None:
                try:
                    self.content.areas.pop(area_id)
                except KeyError:
                    raise PlanPatchError(f"area[id={area_id.hex}] does not exist")
            elif (old_area := self.content.areas.get(area_id)) is None:
                try:
                    self.content.areas[area_id] = Area(**area.model_dump())
                except ValidationError:
                    raise PlanPatchError(f"area[id={area_id.hex}] must be full")
            else:
                self.content.areas[area_id] = self._merge(old_area, area)

        self.updated_at = datetime.now(tz=timezone.utc)

    @staticmethod
    def _merge(a: BaseModel, b: BaseModel) -> Any:
        for k, v in b.model_dump().items():
            if v is not None:
                a.__setattr__(k, v)
        return a
