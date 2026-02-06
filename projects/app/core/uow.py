from abc import ABC, abstractmethod
from typing import Any

from app.core.account import AccountRepository
from app.core.plan import PlanRepository
from app.core.project import ProjectRepository


class UnitOfWork(ABC):
    accounts: AccountRepository
    projects: ProjectRepository
    plans: PlanRepository

    async def __aenter__(self) -> "UnitOfWork": ...

    async def __aexit__(self, exc_type: Any, exc: Any, traceback: Any):
        if exc:
            await self.rollback()
        else:
            await self.commit()

    @abstractmethod
    async def rollback(self) -> None: ...

    @abstractmethod
    async def commit(self) -> None: ...
