from urllib.parse import quote

from functools2 import async_lru_cache  # type: ignore
from httpx import AsyncClient
from pydantic import RootModel

from app.core.facade import SystemFacade
from app.core.models import Furniture, Plan, Project


class GatewayFacade(SystemFacade):
    def __init__(self, client: AsyncClient, account_header: str):
        self.client = client
        self.account_header = account_header

    async def find_project(self, account_id: str, project_id: str) -> Project | None:
        resp = await self.client.get(
            f"/projects/{project_id}",
            headers={self.account_header: account_id},
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        project = Project.model_validate(resp.json())
        return project

    async def find_plan(self, account_id: str, plan_id: str) -> Plan | None:
        resp = await self.client.get(
            f"/plans/{plan_id}",
            headers={self.account_header: account_id},
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        plan = Plan.model_validate(resp.json())
        return plan

    async def match_furniture(self, description: str, count: int) -> list[Furniture]:
        resp = await self.client.get(
            f"/catalog/like?description={quote(description)}&k={count}",
        )
        resp.raise_for_status()
        model = RootModel[list[Furniture]].model_validate(resp.json())
        return model.root

    @async_lru_cache(maxsize=100, ttl=3600)
    async def find_furniture(self, furniture_id: str) -> Furniture | None:
        resp = await self.client.get(
            f"/catalog/furniture/{furniture_id}",
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        model = Furniture.model_validate(resp.json())
        return model
