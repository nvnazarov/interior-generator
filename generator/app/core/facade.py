from abc import ABC, abstractmethod

from app.core.models import Furniture, Plan, Project


class SystemFacade(ABC):
    @abstractmethod
    async def find_project(
        self, account_id: str, project_id: str
    ) -> Project | None: ...

    @abstractmethod
    async def find_plan(self, account_id: str, plan_id: str) -> Plan | None: ...

    @abstractmethod
    async def create_plan(self, account_id: str, project_id: str) -> Plan: ...

    @abstractmethod
    async def find_furniture(self, description: str) -> Furniture: ...
