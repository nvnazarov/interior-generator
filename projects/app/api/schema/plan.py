from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.core.plan import Patch as CorePatch
from app.core.plan import Plan as CorePlan


class Furniture(BaseModel):
    id: str
    x: int
    y: int
    z: int
    yaw: int


class Area(BaseModel):
    id: str
    type: str
    x: int
    y: int
    w: int
    h: int


class Content(BaseModel):
    furniture: dict[str, Furniture] = {}
    areas: dict[str, Area] = {}


class FurniturePatch(BaseModel):
    id: str
    x: int | None = None
    y: int | None = None
    z: int | None = None
    yaw: int | None = None


class AreaPatch(BaseModel):
    id: str
    type: str | None = None
    x: int | None = None
    y: int | None = None
    w: int | None = None
    h: int | None = None


class ContentPatch(BaseModel):
    furniture: dict[str, FurniturePatch | None] = {}
    areas: dict[str, AreaPatch | None] = {}


class Patch(BaseModel):
    name: str | None = None
    content: ContentPatch | None = None

    def to_core(self) -> CorePatch:
        return CorePatch(**self.model_dump())


class Plan(BaseModel):
    id: UUID
    project_id: UUID
    name: str = Field(max_length=256)
    revision: int
    content: Content
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def from_core(plan: CorePlan) -> "Plan":
        return Plan(**plan.model_dump())
