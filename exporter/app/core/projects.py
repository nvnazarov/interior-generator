from typing import AsyncIterable
from abc import ABC, abstractmethod
from app.core.models import Project, Plan


class ProjectsService(ABC):
    @abstractmethod
    async def find_project_by_id(
        self, account_id: str, project_id: str
    ) -> Project | None: ...

    @abstractmethod
    def iter_plans_in_project(
        self, account_id: str, project_id: str
    ) -> AsyncIterable[Plan]: ...
