from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, ValidationError

from app.core.util import now


class PlanRevisionError(Exception): ...


class PlanPatchError(Exception): ...


class Plan(BaseModel):
    class Patch(BaseModel):
        class Content(BaseModel):
            class Furniture(BaseModel):
                furniture_id: str | None = None
                x: int | None = None
                y: int | None = None
                z: int | None = None
                yaw: float | None = None

            class Area(BaseModel):
                class Point(BaseModel):
                    x: int
                    y: int

                type: str | None = None
                points: list[Point] | None = None

            furniture: dict[str, Furniture | None] = Field(default_factory=dict)
            areas: dict[str, Area | None] = Field(default_factory=dict)

        name: str | None = None
        content: Content | None = None

    class Content(BaseModel):
        class Furniture(BaseModel):
            furniture_id: str
            x: int
            y: int
            z: int
            yaw: float

        class Area(BaseModel):
            class Point(BaseModel):
                x: int
                y: int

            type: str
            points: list[Point]

        furniture: dict[str, Furniture] = Field(default_factory=dict)
        areas: dict[str, Area] = Field(default_factory=dict)

    id: str
    project_id: str
    revision: int = 0
    content: Content = Field(default_factory=Content)
    name: str = Field("", max_length=256)
    created_at: datetime = Field(default_factory=now)
    updated_at: datetime = Field(default_factory=now)

    @staticmethod
    def empty(project_id: str) -> "Plan":
        dt = now()
        return Plan(
            id=uuid4().hex,
            project_id=project_id,
            revision=0,
            name="",
            created_at=dt,
            updated_at=dt,
        )

    def patch(self, patch: Patch, revision: int) -> None:
        if revision != self.revision:
            raise PlanRevisionError

        if patch.name is not None:
            self.name = patch.name
        if patch.content is not None:
            for furniture_id, furniture in patch.content.furniture.items():
                if furniture is None:
                    try:
                        self.content.furniture.pop(furniture_id)
                    except KeyError:
                        continue
                elif (
                    old_furniture := self.content.furniture.get(furniture_id)
                ) is None:
                    try:
                        self.content.furniture[furniture_id] = Plan.Content.Furniture(
                            **furniture.model_dump()
                        )
                    except ValidationError:
                        raise PlanPatchError(
                            f"furniture[id={furniture_id}] must be full"
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
                        continue
                elif (old_area := self.content.areas.get(area_id)) is None:
                    try:
                        self.content.areas[area_id] = Plan.Content.Area(
                            **area.model_dump()
                        )
                    except ValidationError:
                        raise PlanPatchError(f"area[id={area_id}] must be full")
                else:
                    self.content.areas[area_id] = self._merge(old_area, area)

        self.revision += 1
        self.updated_at = now()

    @staticmethod
    def _merge(a: BaseModel, b: BaseModel) -> Any:
        for k, v in b.model_dump().items():
            if v is not None:
                a.__setattr__(k, v)
        return a


class PlansRepository(ABC):
    @abstractmethod
    async def find(self, plan_id: str) -> Plan | None: ...

    @abstractmethod
    async def save(self, plan: Plan) -> None: ...

    @abstractmethod
    async def find_without_content(self, plan_id: str) -> Plan | None: ...

    @abstractmethod
    async def save_without_content(self, plan: Plan) -> None: ...

    @abstractmethod
    async def delete(self, plan: Plan) -> None: ...

    @abstractmethod
    async def in_project(self, project_id: str) -> list[Plan]: ...
