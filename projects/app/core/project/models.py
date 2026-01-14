from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.core.project.errors import ProjectsPerAccountLimitExceededError


class Quota(BaseModel):
    account_id: UUID
    max_projects_count: int
    current_projects_count: int = Field(ge=0)
    version: int

    @staticmethod
    def create(account_id: UUID, max_projects_count: int) -> "Quota":
        return Quota(
            account_id=account_id,
            max_projects_count=max_projects_count,
            current_projects_count=0,
            version=0,
        )

    def increase(self):
        if self.current_projects_count >= self.max_projects_count:
            raise ProjectsPerAccountLimitExceededError
        self.current_projects_count += 1

    def decrease(self):
        if self.current_projects_count > 0:
            self.current_projects_count -= 1


class Project(BaseModel):
    id: UUID
    account_id: UUID
    name: str = Field(max_length=256)
    description: str = Field(max_length=2048)
    pinned: bool
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def create(account_id: UUID) -> "Project":
        dt = datetime.now(tz=timezone.utc)
        return Project(
            id=uuid4(),
            account_id=account_id,
            name="",
            description="",
            pinned=False,
            created_at=dt,
            updated_at=dt,
        )

    def pin(self):
        self.pinned = True
        self.updated_at = datetime.now(tz=timezone.utc)

    def unpin(self):
        self.pinned = False
        self.updated_at = datetime.now(tz=timezone.utc)

    def rename(self, name: str):
        self.name = name
        self.updated_at = datetime.now(tz=timezone.utc)

    def change_description(self, description: str):
        self.description = description
        self.updated_at = datetime.now(tz=timezone.utc)
