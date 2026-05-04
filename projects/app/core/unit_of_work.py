from abc import ABC, abstractmethod
from typing import AsyncContextManager

from app.core.account import AccountsRepository
from app.core.plan import PlansRepository
from app.core.project import ProjectsRepository


class UnitOfWork(ABC):
    accounts: AccountsRepository
    projects: ProjectsRepository
    plans: PlansRepository

    @abstractmethod
    async def rollback(self) -> None: ...

    @abstractmethod
    async def commit(self) -> None: ...


class UnitOfWorkFactory(ABC):
    @abstractmethod
    def begin(self) -> AsyncContextManager[UnitOfWork]: ...
