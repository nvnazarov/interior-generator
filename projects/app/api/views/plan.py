from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

import app.core.plan.models as models


class Furniture(BaseModel):
    id: UUID
    x: int
    y: int
    z: int
    yaw: int


class Area(BaseModel):
    id: UUID
    type: str
    x: int
    y: int
    w: int
    h: int


class Content(BaseModel):
    furniture: dict[UUID, Furniture] = {}
    areas: dict[UUID, Area] = {}


class FurniturePatch(BaseModel):
    id: UUID
    x: int | None = None
    y: int | None = None
    z: int | None = None
    yaw: int | None = None


class AreaPatch(BaseModel):
    id: UUID
    type: str | None = None
    x: int | None = None
    y: int | None = None
    w: int | None = None
    h: int | None = None


class Plan(BaseModel):
    id: UUID
    name: str = Field(max_length=256)
    version: int
    content: Content
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def from_model(plan: models.Plan) -> "Plan":
        return Plan(**plan.model_dump())


class PlanNoContent(BaseModel):
    id: UUID
    name: str = Field(max_length=256)
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def from_model(plan: models.Plan) -> "PlanNoContent":
        return PlanNoContent(**plan.model_dump())


class Patch(BaseModel):
    version: int = 0
    furniture: dict[UUID, FurniturePatch | None] = {}
    areas: dict[UUID, AreaPatch | None] = {}

    def to_model(self) -> models.Patch:
        return models.Patch(**self.model_dump())
