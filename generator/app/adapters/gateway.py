from httpx import AsyncClient
from urllib.parse import quote
from pydantic import RootModel

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

    async def create_plan(self, account_id: str, project_id: str) -> tuple[Plan, str]:
        resp = await self.client.post(
            f"/projects/{project_id}/plans",
            headers={"x-account-id": account_id},
        )
        resp.raise_for_status()
        plan = Plan.model_validate(resp.json())
        etag = resp.headers["etag"]
        return plan, etag

    async def patch_plan(
        self, account_id: str, plan_id: str, etag: str, patch: Plan.Patch
    ) -> str:
        resp = await self.client.patch(
            f"/plans/{plan_id}",
            headers={"x-account-id": account_id, "if-match": etag},
            json=patch.model_dump(),
        )
        resp.raise_for_status()
        new_etag = resp.headers["etag"]
        return new_etag

    async def find_furniture(self, description: str, count: int) -> list[Furniture]:
        resp = await self.client.get(
            f"/catalog/like?description={quote(description)}&k={count}",
        )
        resp.raise_for_status()
        model = RootModel[list[Furniture]].model_validate(resp.json())
        return model.root
