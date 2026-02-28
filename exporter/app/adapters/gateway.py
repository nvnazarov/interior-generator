from typing import AsyncIterable
from uuid import UUID

from httpx import AsyncClient
from pydantic import RootModel

from app.core.exporter import Repository
from app.core.models import Plan, Project


class APIGatewayAdapter(Repository):
    def __init__(self, client: AsyncClient):
        self.client = client

    async def get_project(self, account_id: UUID, project_id: UUID) -> Project | None:
        resp = await self.client.get(
            f"/projects/{project_id}",
            headers={"x-account-id": account_id.hex},
        )
        if resp.status_code == 404:
            return None
        project = Project.model_validate(resp.json())
        return project

    async def get_plan(self, account_id: UUID, plan_id: UUID) -> Plan | None:
        resp = await self.client.get(
            f"/plans/{plan_id}",
            headers={"x-account-id": account_id.hex},
        )
        if resp.status_code == 404:
            return None
        plan = Plan.model_validate(resp.json())
        return plan

    async def get_plans_of_project(
        self, account_id: UUID, project_id: UUID
    ) -> AsyncIterable[Plan]:
        resp = await self.client.get(
            f"/projects/{project_id}/plans",
            headers={"x-account-id": account_id.hex},
        )
        plans_meta = RootModel[list[Plan]].model_validate(resp.json()).root
        for meta in plans_meta:
            resp = await self.client.get(
                f"/plans/{meta.id}",
                headers={"x-account-id": account_id.hex},
            )
            if resp.status_code == 404:
                continue
            plan = Plan.model_validate(resp.json())
            yield plan
