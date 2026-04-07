from httpx import AsyncClient

from app.core.facade import SystemFacade
from app.core.models import Furniture, Plan, Project


class GatewayFacade(SystemFacade):
    def __init__(self, client: AsyncClient):
        self.client = client

    async def find_project(self, account_id: str, project_id: str) -> Project | None:
        resp = await self.client.get(
            f"/projects/{project_id}",
            headers={"x-account-id": account_id},
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        project = Project.model_validate(resp.json())
        return project

    async def find_plan(self, account_id: str, plan_id: str) -> Plan | None:
        resp = await self.client.get(
            f"/plans/{plan_id}",
            headers={"x-account-id": account_id},
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        plan = Plan.model_validate(resp.json())
        return plan

    async def create_plan(self, account_id: str, project_id: str) -> Plan: ...

    async def find_furniture(self, description: str) -> Furniture: ...
