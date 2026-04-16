from abc import ABC, abstractmethod
from typing import Awaitable

from app.core.models import Furniture, Plan, Project


class SystemFacade(ABC):
    @abstractmethod
    async def find_project(
        self, account_id: str, project_id: str
    ) -> Project | None: ...

    @abstractmethod
    async def find_plan(self, account_id: str, plan_id: str) -> Plan | None: ...

    @abstractmethod
    async def create_plan(
        self, account_id: str, project_id: str
    ) -> tuple[Plan, str]: ...

    @abstractmethod
    async def patch_plan(
        self, account_id: str, plan_id: str, etag: str, patch: Plan.Patch
    ) -> str: ...

    @abstractmethod
    async def match_furniture(
        self, description: str, count: int
    ) -> list[Furniture]: ...

    @abstractmethod
    def find_furniture(self, furniture_id: str) -> Awaitable[Furniture | None]: ...
