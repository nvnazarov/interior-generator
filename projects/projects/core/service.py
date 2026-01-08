from typing import Any, AsyncContextManager, Callable
from uuid import UUID

from projects.core.models import Project, Plan
from projects.core.errors import (
    ProjectsPerAccountLimitExceededError,
    PlansPerProjectLimitExceededError,
)


class IProjectUnitOfWork:
    async def create_project(self, account_id: UUID) -> Project:
        raise NotImplementedError

    async def get_project_by_id(
        self, account_id: UUID, project_id: UUID
    ) -> Project | None:
        raise NotImplementedError

    async def delete_project(self, account_id: UUID, project_id: UUID) -> None:
        raise NotImplementedError

    async def patch_project(
        self, account_id: UUID, project_id: UUID, **kwargs: Any
    ) -> None:
        raise NotImplementedError

    async def get_all_projects(self, account_id: UUID) -> list[Project]:
        raise NotImplementedError

    async def pin_project(self, account_id: UUID, project_id: UUID) -> None:
        raise NotImplementedError

    async def unpin_project(self, account_id: UUID, project_id: UUID) -> None:
        raise NotImplementedError

    async def get_total_projects_count(self, account_id: UUID) -> int:
        raise NotImplementedError

    async def commit(self) -> None:
        raise NotImplementedError


class ProjectService:
    def __init__(
        self,
        unit_of_work_factory: Callable[[], AsyncContextManager[IProjectUnitOfWork]],
        max_projects_per_account: int = 20,
    ):
        self.uow_factory = unit_of_work_factory
        self.max_projects_per_account = max_projects_per_account

    async def create_project(self, account_id: UUID) -> Project:
        async with self.uow_factory() as uow:
            total_projects_count = await uow.get_total_projects_count(account_id)
            if total_projects_count >= self.max_projects_per_account:
                raise ProjectsPerAccountLimitExceededError
            project = await uow.create_project(account_id)
            await uow.commit()
        return project

    async def get_project_by_id(
        self, account_id: UUID, project_id: UUID
    ) -> Project | None:
        async with self.uow_factory() as uow:
            return await uow.get_project_by_id(account_id, project_id)

    async def delete_project(self, account_id: UUID, project_id: UUID) -> None:
        async with self.uow_factory() as uow:
            await uow.delete_project(account_id, project_id)
            await uow.commit()

    async def patch_project(
        self, account_id: UUID, project_id: UUID, **kwargs: Any
    ) -> None:
        async with self.uow_factory() as uow:
            await uow.patch_project(account_id, project_id, **kwargs)
            await uow.commit()

    async def get_all_projects(self, account_id: UUID) -> list[Project]:
        async with self.uow_factory() as uow:
            return await uow.get_all_projects(account_id)

    async def pin_project(self, account_id: UUID, project_id: UUID) -> None:
        async with self.uow_factory() as uow:
            await uow.pin_project(account_id, project_id)
            await uow.commit()

    async def unpin_project(self, account_id: UUID, project_id: UUID) -> None:
        async with self.uow_factory() as uow:
            await uow.unpin_project(account_id, project_id)
            await uow.commit()


class IPlanUnitOfWork:
    async def get_all_project_plans(
        self, account_id: UUID, project_id: UUID
    ) -> list[Plan]:
        raise NotImplementedError

    async def get_project_plans_count(self, account_id: UUID, project_id: UUID) -> int:
        raise NotImplementedError

    async def create_plan(
        self, account_id: UUID, project_id: UUID, **kwargs: Any
    ) -> Plan:
        raise NotImplementedError

    async def get_plan_by_id(self, account_id: UUID, plan_id: UUID) -> Plan | None:
        raise NotImplementedError

    async def delete_plan(self, account_id: UUID, plan_id: UUID) -> None:
        raise NotImplementedError

    async def __aenter__(self) -> "IPlanUnitOfWork":
        raise NotImplementedError

    async def __aexit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        raise NotImplementedError

    async def commit(self) -> None:
        raise NotImplementedError


class PlanService:
    def __init__(
        self,
        unit_of_work: IPlanUnitOfWork,
        max_plans_per_project: int = 20,
    ):
        self.unit_of_work = unit_of_work
        self.max_plans_per_project = max_plans_per_project

    async def get_all_project_plans(
        self, account_id: UUID, project_id: UUID
    ) -> list[Plan]:
        async with self.unit_of_work as uow:
            return await uow.get_all_project_plans(account_id, project_id)

    async def create_plan(
        self, account_id: UUID, project_id: UUID, **kwargs: Any
    ) -> Plan:
        async with self.unit_of_work as uow:
            plans_count = await uow.get_project_plans_count(account_id, project_id)
            if plans_count >= self.max_plans_per_project:
                raise PlansPerProjectLimitExceededError
            plan = await uow.create_plan(account_id, project_id, **kwargs)
            await uow.commit()
        return plan

    async def get_plan_by_id(self, account_id: UUID, plan_id: UUID) -> Plan | None:
        async with self.unit_of_work as uow:
            return await uow.get_plan_by_id(account_id, plan_id)

    async def delete_plan(self, account_id: UUID, plan_id: UUID) -> None:
        async with self.unit_of_work as uow:
            await uow.delete_plan(account_id, plan_id)
            await uow.commit()

    async def patch_plan(
        self, account_id: UUID, plan_id: UUID, operations: dict[str, str]
    ) -> None:
        raise
