from typing import AsyncIterable
from uuid import UUID

from httpx import AsyncClient

from app.core.exporter import IProjectsRepository
from app.core.models import Plan


class ProjectsServiceAdapter(IProjectsRepository):
    def __init__(self, client: AsyncClient):
        self.client = client

    def get_plans(self, project_id: UUID, account_id: UUID) -> AsyncIterable[Plan]:
        # plans = await self.client.get(
        #     f"/projects/{project_id}/plans",
        #     headers={"x-account-id": account_id.hex},
        # )
        # for plan_id in plans:
        #     plan = await self.client.get(
        #         f"/plans/{plan_id}",
        #         headers={"x-account-id": account_id.hex},
        #     )
        #     shell = await self.client.get(
        #         f"/shells/{shell_id}",
        #         headers={"x-account-id": account_id.hex},
        #     )
        #     await asyncio.sleep(0.1)
        #     yield Plan()
        raise
