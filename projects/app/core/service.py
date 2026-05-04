from app.core.account import Account
from app.core.plan import Plan
from app.core.project import Project
from app.core.unit_of_work import UnitOfWorkFactory


class AccessDeniedError(Exception): ...


class ProjectNotFoundError(Exception): ...


class PlanNotFoundError(Exception): ...


class Service:
    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        *,
        projects_limit: int = 20,
        plans_limit: int = 20,
    ):
        self._factory = uow_factory
        self._plans_limit = plans_limit
        self._projects_limit = projects_limit

    async def create_project(self, account_id: str) -> Project:
        async with self._factory.begin() as u:
            account = await u.accounts.find(account_id)
            if account is None:
                account = Account.create(
                    account_id, projects_limit=self._projects_limit
                )
            project = account.create_project(plans_limit=self._plans_limit)
            await u.accounts.save(account)
            await u.projects.save(project)
            await u.commit()
            return project

    async def get_project(self, account_id: str, project_id: str) -> Project:
        async with self._factory.begin() as u:
            project = await u.projects.find(project_id)
            if project is None:
                raise ProjectNotFoundError
            if not project.can_be_read_by(account_id):
                raise AccessDeniedError
            return project

    async def delete_project(self, account_id: str, project_id: str) -> None:
        async with self._factory.begin() as u:
            account = await u.accounts.find(account_id)
            if account is None:
                raise ProjectNotFoundError
            project = await u.projects.find_without_content(project_id)
            if project is None:
                raise ProjectNotFoundError
            if not project.is_owned_by(account_id):
                raise AccessDeniedError
            account.delete_project(project_id)
            await u.accounts.save(account)
            await u.projects.delete(project_id)
            await u.commit()

    async def patch_project(
        self,
        account_id: str,
        project_id: str,
        *,
        patch: Project.Patch,
        revision: int,
    ) -> Project:
        async with self._factory.begin() as u:
            no_content = patch.content is None
            if no_content:
                project = await u.projects.find_without_content(project_id)
            else:
                project = await u.projects.find(project_id)
            if project is None:
                raise ProjectNotFoundError
            if not project.is_owned_by(account_id):
                raise AccessDeniedError
            project.patch(patch, revision)
            if no_content:
                await u.projects.save_without_content(project)
            else:
                await u.projects.save(project)
            await u.commit()
            return project

    async def get_projects_owned_by_account(self, account_id: str) -> list[Project]:
        async with self._factory.begin() as u:
            return await u.projects.owned_by_account(account_id)

    async def publish_project(self, project_id: str, account_id: str) -> Project:
        async with self._factory.begin() as u:
            project = await u.projects.find_without_content(project_id)
            if project is None:
                raise ProjectNotFoundError
            if not project.is_owned_by(account_id):
                raise AccessDeniedError
            project.publish()
            await u.projects.save_without_content(project)
            await u.commit()
            return project

    async def unublish_project(self, project_id: str, account_id: str) -> Project:
        async with self._factory.begin() as u:
            project = await u.projects.find_without_content(project_id)
            if project is None:
                raise ProjectNotFoundError
            if not project.is_owned_by(account_id):
                raise AccessDeniedError
            project.unpublish()
            await u.projects.save_without_content(project)
            await u.commit()
            return project

    async def create_plan(self, account_id: str, project_id: str) -> Plan:
        async with self._factory.begin() as u:
            project = await u.projects.find_without_content(project_id)
            if project is None:
                raise ProjectNotFoundError
            if not project.is_owned_by(account_id):
                raise AccessDeniedError
            plan = project.create_plan()
            await u.projects.save_without_content(project)
            await u.plans.save(plan)
            await u.commit()
            return plan

    async def get_plan(self, account_id: str, plan_id: str) -> Plan:
        async with self._factory.begin() as u:
            plan = await u.plans.find(plan_id)
            if plan is None:
                raise PlanNotFoundError
            project = await u.projects.find_without_content(plan.project_id)
            if project is None:
                raise PlanNotFoundError
            if not project.can_be_read_by(account_id):
                raise AccessDeniedError
            return plan

    async def delete_plan(self, account_id: str, plan_id: str) -> None:
        async with self._factory.begin() as u:
            plan = await u.plans.find(plan_id)
            if plan is None:
                raise PlanNotFoundError
            project = await u.projects.find_without_content(plan.project_id)
            if project is None:
                raise PlanNotFoundError
            if not project.is_owned_by(account_id):
                raise AccessDeniedError
            project.delete_plan(plan_id)
            await u.projects.save_without_content(project)
            await u.plans.delete(plan)
            await u.commit()

    async def patch_plan(
        self, account_id: str, plan_id: str, *, patch: Plan.Patch, revision: int
    ) -> Plan:
        async with self._factory.begin() as u:
            no_content = patch.content is None
            if no_content:
                plan = await u.plans.find_without_content(plan_id)
            else:
                plan = await u.plans.find(plan_id)
            if plan is None:
                raise PlanNotFoundError
            project = await u.projects.find_without_content(plan.project_id)
            if project is None:
                raise PlanNotFoundError
            if not project.is_owned_by(account_id):
                raise AccessDeniedError
            plan.patch(patch, revision)
            if no_content:
                await u.plans.save_without_content(plan)
            else:
                await u.plans.save(plan)
            await u.commit()
            return plan

    async def get_plans_in_project(
        self, account_id: str, project_id: str
    ) -> list[Plan]:
        async with self._factory.begin() as u:
            project = await u.projects.find_without_content(project_id)
            if project is None:
                raise ProjectNotFoundError
            if not project.can_be_read_by(account_id):
                raise AccessDeniedError
            return await u.plans.in_project(project_id)
