from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.core.project import models


class Patch(BaseModel):
    name: str | None = Field(None, max_length=256)
    description: str | None = Field(None, max_length=2048)


class Project(BaseModel):
    id: UUID
    name: str = Field(max_length=256)
    description: str = Field(max_length=2048)
    pinned: bool
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def from_model(project: models.Project) -> "Project":
        return Project(**project.model_dump())
