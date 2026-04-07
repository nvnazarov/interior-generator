from abc import ABC, abstractmethod
from uuid import uuid4

from pydantic import BaseModel

from app.core.project import Project
from app.core.util import now


class ProjectsLimitExceeded(Exception): ...


class NoProjects(Exception): ...


class Account(BaseModel):
    id: str
    projects_count: int = 0
    projects_limit: int = 0

    @staticmethod
    def create(
        account_id: str, *, projects_count: int = 0, projects_limit: int = 0
    ) -> "Account":
        return Account(
            id=account_id,
            projects_count=projects_count,
            projects_limit=projects_limit,
        )

    def create_project(
        self, *, plans_limit: int, name: str = "", description: str = ""
    ) -> Project:
        if self.projects_count >= self.projects_limit:
            raise ProjectsLimitExceeded
        self.projects_count += 1
        dt = now()
        return Project(
            id=uuid4().hex,
            account_id=self.id,
            name=name,
            description=description,
            created_at=dt,
            updated_at=dt,
            plans_count=0,
            plans_limit=plans_limit,
        )

    def delete_project(self, project_id: str) -> None:
        if self.projects_count == 0:
            raise NoProjects
        self.projects_count = max(0, self.projects_count - 1)


class AccountRepository(ABC):
    @abstractmethod
    async def get(self, account_id: str) -> Account | None: ...

    @abstractmethod
    async def save(self, account: Account) -> None: ...
