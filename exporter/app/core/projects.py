from abc import ABC, abstractmethod
from typing import AsyncIterable

from app.core.models import Plan, Project


class ProjectsService(ABC):
    @abstractmethod
    async def find_project_by_id(
        self, account_id: str, project_id: str
    ) -> Project | None: ...

    @abstractmethod
    def iter_plans_in_project(
        self, account_id: str, project_id: str
    ) -> AsyncIterable[Plan]: ...
