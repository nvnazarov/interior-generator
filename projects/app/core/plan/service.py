from abc import ABC, abstractmethod
from typing import Any, Callable
from uuid import UUID

from app.core.plan.errors import PlanNotFoundError, ProjectNotFound
from app.core.plan.models import Patch, Plan, Quota


class IQuotaRepository(ABC):
    @abstractmethod
    async def get(self, project_id: UUID) -> Quota | None: ...

    @abstractmethod
    async def save(self, quota: Quota) -> None: ...


class IPlansRepository(ABC):
    @abstractmethod
    async def get(self, plan_id: UUID, account_id: UUID) -> Plan | None: ...

    @abstractmethod
    async def save(self, plan: Plan) -> None: ...

    @abstractmethod
    async def save_content(self, plan: Plan) -> None: ...

    @abstractmethod
    async def get_no_content(self, plan_id: UUID, account_id: UUID) -> Plan | None: ...

    @abstractmethod
    async def save_no_content(self, plan: Plan) -> None: ...

    @abstractmethod
    async def get_all_no_content(
        self, project_id: UUID, account_id: UUID
    ) -> list[Plan]: ...

    @abstractmethod
    async def delete(self, plan_id: UUID) -> None: ...

    @abstractmethod
    async def is_project_owned_by_account(
        self, project_id: UUID, account_id: UUID
    ) -> bool: ...


class IPlansUnitOfWork(ABC):
    quota: IQuotaRepository
    plans: IPlansRepository

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


class PlanService:
    def __init__(
        self,
        uow_factory: Callable[[], IPlansUnitOfWork],
        max_plans_per_project: int = 20,
    ):
        self.uow_factory = uow_factory
        self.max_plans_per_project = max_plans_per_project

    async def create_plan(
        self, account_id: UUID, project_id: UUID, shell_id: UUID
    ) -> Plan:
        async with self.uow_factory() as uow:
            if not await uow.plans.is_project_owned_by_account(project_id, account_id):
                raise ProjectNotFound
            quota = await uow.quota.get(project_id)
            if not quota:
                quota = Quota.create(project_id, self.max_plans_per_project)
            quota.increase()
            await uow.quota.save(quota)
            plan = Plan.create(project_id, shell_id)
            await uow.plans.save(plan)
            return plan

    async def get_plan_by_id(self, account_id: UUID, plan_id: UUID) -> Plan | None:
        async with self.uow_factory() as uow:
            return await uow.plans.get(plan_id, account_id)

    async def get_all_project_plans(
        self, account_id: UUID, project_id: UUID
    ) -> list[Plan]:
        async with self.uow_factory() as uow:
            return await uow.plans.get_all_no_content(project_id, account_id)

    async def rename_plan(self, account_id: UUID, plan_id: UUID, name: str) -> None:
        async with self.uow_factory() as uow:
            plan = await uow.plans.get_no_content(plan_id, account_id)
            if plan is None:
                raise PlanNotFoundError
            plan.rename(name)
            await uow.plans.save(plan)

    async def patch_plan(self, account_id: UUID, plan_id: UUID, patch: Patch) -> int:
        async with self.uow_factory() as uow:
            plan = await uow.plans.get(plan_id, account_id)
            if plan is None:
                raise PlanNotFoundError
            plan.patch(patch)
            await uow.plans.save_content(plan)
            return plan.version

    async def delete_plan(self, account_id: UUID, plan_id: UUID) -> None:
        async with self.uow_factory() as uow:
            plan = await uow.plans.get_no_content(plan_id, account_id)
            if plan is not None:
                quota = await uow.quota.get(plan.project_id)
                if not quota:
                    raise RuntimeError("quota does not exist")
                quota.decrease()
                await uow.quota.save(quota)
                await uow.plans.delete(plan_id)
