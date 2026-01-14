from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.core.plan.errors import (
    PlanPatchError,
    PlansPerProjectLimitExceededError,
    PlanVersionConflictError,
)


class Quota(BaseModel):
    project_id: UUID
    max_plans_count: int
    current_plans_count: int = Field(ge=0)
    version: int

    def increase(self):
        if self.current_plans_count >= self.max_plans_count:
            raise PlansPerProjectLimitExceededError
        self.current_plans_count += 1

    def decrease(self):
        if self.current_plans_count > 0:
            self.current_plans_count -= 1


class Patch(BaseModel):
    version: int = 0
    add_furniture: list[UUID] = []
    del_furnuture: list[UUID] = []


class Content(BaseModel):
    version: int = 0
    furniture: list[str] = []

    def patch(self, patch: Patch):
        if patch.version != self.version:
            raise PlanVersionConflictError
        raise PlanPatchError


class Plan(BaseModel):
    id: UUID
    project_id: UUID
    content: Content
    name: str = Field(max_length=256)
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def create(project_id: UUID) -> "Plan":
        return Plan(
            id=uuid4(),
            project_id=project_id,
            name="",
            content=Content(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    def rename(self, name: str):
        self.name = name
        self.updated_at = datetime.now()
