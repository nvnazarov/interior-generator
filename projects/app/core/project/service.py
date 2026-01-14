from abc import ABC, abstractmethod
from typing import Any, Callable
from uuid import UUID

from app.core.project.errors import ProjectNotFoundError
from app.core.project.models import Project, Quota


class IProjectsRepository(ABC):
    @abstractmethod
    async def get(self, project_id: UUID) -> Project | None: ...

    @abstractmethod
    async def all(self, account_id: UUID) -> list[Project]: ...

    @abstractmethod
    async def save(self, project: Project) -> None: ...

    @abstractmethod
    async def delete(self, project_id: UUID) -> None: ...


class IQuotaRepository(ABC):
    @abstractmethod
    async def get(self, account_id: UUID) -> Quota | None: ...

    @abstractmethod
    async def save(self, quota: Quota) -> None: ...


class IProjectsUnitOfWork(ABC):
    quota: IQuotaRepository
    projects: IProjectsRepository

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, traceback: Any):
        if exc:
            await self.rollback()
        else:
            await self.commit()

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...


class ProjectService:
    def __init__(
        self,
        uow_factory: Callable[[], IProjectsUnitOfWork],
        max_projects_per_account: int = 20,
    ):
        self.uow_factory = uow_factory
        self.max_projects_per_account = max_projects_per_account

    async def create_project(self, account_id: UUID) -> Project:
        async with self.uow_factory() as uow:
            quota = await uow.quota.get(account_id)
            if quota is None:
                quota = Quota.create(account_id, self.max_projects_per_account)
            quota.increase()
            await uow.quota.save(quota)
            project = Project.create(account_id)
            await uow.projects.save(project)
            return project

    async def get_project_by_id(
        self, account_id: UUID, project_id: UUID
    ) -> Project | None:
        async with self.uow_factory() as uow:
            project = await uow.projects.get(project_id)
            if project is None or project.account_id != account_id:
                return None
            return project

    async def delete_project(self, account_id: UUID, project_id: UUID) -> None:
        async with self.uow_factory() as uow:
            project = await uow.projects.get(project_id)
            if project is not None and project.account_id == account_id:
                quota = await uow.quota.get(account_id)
                quota.decrease()
                await uow.quota.save(quota)
                await uow.projects.delete(project_id)

    async def patch_project(
        self, account_id: UUID, project_id: UUID, **kwargs: str
    ) -> None:
        async with self.uow_factory() as uow:
            project = await uow.projects.get(project_id)
            if project is None or project.account_id != account_id:
                raise ProjectNotFoundError
            if kwargs.get("name") is not None:
                project.rename(kwargs["name"])
            if kwargs.get("description") is not None:
                project.change_description(kwargs["description"])
            await uow.projects.save(project)

    async def get_all_projects(self, account_id: UUID) -> list[Project]:
        async with self.uow_factory() as uow:
            return await uow.projects.all(account_id)

    async def pin_project(self, account_id: UUID, project_id: UUID) -> None:
        async with self.uow_factory() as uow:
            project = await uow.projects.get(project_id)
            if project is None or project.account_id != account_id:
                raise ProjectNotFoundError
            project.pin()
            await uow.projects.save(project)

    async def unpin_project(self, account_id: UUID, project_id: UUID) -> None:
        async with self.uow_factory() as uow:
            project = await uow.projects.get(project_id)
            if project is None or project.account_id != account_id:
                raise ProjectNotFoundError
            project.unpin()
            await uow.projects.save(project)
