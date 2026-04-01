from uuid import UUID

from app.core.account import Account
from app.core.plan import Patch as PlanPatch
from app.core.plan import Plan
from app.core.project import Patch as ProjectPatch
from app.core.project import Project
from app.core.uow import UnitOfWork


class ProjectNotFoundError(Exception): ...


class PlanNotFoundError(Exception): ...


class Service:
    def __init__(
        self,
        uow_factory: UnitOfWork,
        *,
        projects_limit: int = 20,
        plans_limit: int = 20,
    ):
        self.uow_factory = uow_factory
        self.plans_limit = plans_limit
        self.projects_limit = projects_limit

    async def create_project(self, account_id: str) -> Project:
        async with self.uow_factory as u:
            account = await u.accounts.get(account_id)
            if account is None:
                account = Account.create(account_id, projects_limit=self.projects_limit)
            project = account.create_project(plans_limit=self.plans_limit)
            await u.accounts.save(account)
            await u.projects.save(project)
            return project

    async def get_project(self, account_id: str, project_id: UUID) -> Project:
        async with self.uow_factory as u:
            project = await u.projects.get(project_id)
            if project is None or not project.can_be_read_by(account_id):
                raise ProjectNotFoundError
            return project

    async def delete_project(self, account_id: str, project_id: UUID) -> None:
        async with self.uow_factory as u:
            account = await u.accounts.get(account_id)
            if account is None:
                raise ProjectNotFoundError
            project = await u.projects.get_without_content(project_id)
            if project is None or not project.is_owned_by(account_id):
                raise ProjectNotFoundError
            account.delete_project(project_id)
            await u.accounts.save(account)
            await u.projects.delete(project_id)

    async def patch_project(
        self,
        account_id: str,
        project_id: UUID,
        *,
        patch: ProjectPatch,
        revision: int,
    ) -> Project:
        async with self.uow_factory as u:
            if patch.content is None:
                project = await u.projects.get_without_content(project_id)
            else:
                project = await u.projects.get(project_id)
            if project is None or not project.is_owned_by(account_id):
                raise ProjectNotFoundError
            project.patch(patch, revision)
            if patch.content is None:
                await u.projects.save_without_content(project)
            else:
                await u.projects.save(project)
            return project

    async def get_projects_owned_by_account(self, account_id: str) -> list[Project]:
        async with self.uow_factory as u:
            return await u.projects.get_all_owned_by_account(account_id)

    async def publish_project(self, project_id: UUID, account_id: str) -> None:
        async with self.uow_factory as u:
            project = await u.projects.get_without_content(project_id)
            if project is None or not project.is_owned_by(account_id):
                raise ProjectNotFoundError
            project.publish()
            await u.projects.save_without_content(project)

    async def unublish_project(self, project_id: UUID, account_id: str) -> None:
        async with self.uow_factory as u:
            project = await u.projects.get_without_content(project_id)
            if project is None or not project.is_owned_by(account_id):
                raise ProjectNotFoundError
            project.unpublish()
            await u.projects.save_without_content(project)

    async def create_plan(self, account_id: str, project_id: UUID) -> Plan:
        async with self.uow_factory as u:
            project = await u.projects.get_without_content(project_id)
            if project is None or not project.is_owned_by(account_id):
                raise ProjectNotFoundError
            plan = project.create_plan()
            await u.projects.save(project)
            await u.plans.save(plan)
            return plan

    async def get_plan(self, account_id: str, plan_id: UUID) -> Plan:
        async with self.uow_factory as u:
            plan = await u.plans.get(plan_id)
            if plan is None:
                raise PlanNotFoundError
            project = await u.projects.get_without_content(plan.project_id)
            if project is None or not project.can_be_read_by(account_id):
                raise PlanNotFoundError
            return plan

    async def delete_plan(self, account_id: str, plan_id: UUID) -> None:
        async with self.uow_factory as u:
            plan = await u.plans.get(plan_id)
            if plan is None:
                raise PlanNotFoundError
            project = await u.projects.get_without_content(plan.project_id)
            if project is None or not project.is_owned_by(account_id):
                raise PlanNotFoundError
            project.delete_plan(plan_id)
            await u.projects.save(project)
            await u.plans.delete(plan)

    async def patch_plan(
        self, account_id: str, plan_id: UUID, *, patch: PlanPatch, revision: int
    ) -> Plan:
        async with self.uow_factory as u:
            if patch.content is None:
                plan = await u.plans.get_without_content(plan_id)
            else:
                plan = await u.plans.get(plan_id)
            if plan is None:
                raise PlanNotFoundError
            project = await u.projects.get_without_content(plan.project_id)
            if project is None or not project.is_owned_by(account_id):
                raise PlanNotFoundError
            plan.patch(patch, revision)
            if patch.content is None:
                await u.plans.save_without_content(plan)
            else:
                await u.plans.save(plan)
            return plan

    async def get_plans_of_project(
        self, account_id: str, project_id: UUID
    ) -> list[Plan]:
        async with self.uow_factory as u:
            project = await u.projects.get_without_content(project_id)
            if project is None or not project.can_be_read_by(account_id):
                raise ProjectNotFoundError
            return await u.plans.get_all_of_project(project_id)
