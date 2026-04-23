from httpx import AsyncClient
from pydantic import RootModel
from functools2 import async_lru_cache  # type: ignore

from app.core.catalog import Catalog
from app.core.projects import ProjectsService
from app.core.models import Plan, Project, Furniture


class GatewayCatalog(Catalog):
    def __init__(self, client: AsyncClient):
        self.client = client

    @async_lru_cache(maxsize=100, ttl=3600)
    async def find_furniture_by_id(self, id: str) -> Furniture | None:
        resp = await self.client.get(
            f"/catalog/furniture/{id}",
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        model = Furniture.model_validate(resp.json())
        return model


class GatewayProjectsService(ProjectsService):
    def __init__(self, client: AsyncClient):
        self.client = client

    async def find_project_by_id(
        self, account_id: str, project_id: str
    ) -> Project | None:
        resp = await self.client.get(
            f"/projects/{project_id}",
            headers={"x-account-id": account_id},
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        project = Project.model_validate(resp.json())
        return project

    async def iter_plans_in_project(self, account_id: str, project_id: str):
        resp = await self.client.get(
            f"/projects/{project_id}/plans",
            headers={"x-account-id": account_id},
        )
        resp.raise_for_status()
        partial_plans = RootModel[list[Plan]].model_validate(resp.json()).root
        for partial_plan in partial_plans:
            resp = await self.client.get(
                f"/plans/{partial_plan.id}",
                headers={"x-account-id": account_id},
            )
            if resp.status_code == 404:
                continue
            plan = Plan.model_validate(resp.json())
            yield plan
