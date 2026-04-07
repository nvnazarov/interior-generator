from app.core.facade import SystemFacade
from app.core.models import Furniture, Plan, Project


class GatewayFacade(SystemFacade):
    async def find_project(
        self, account_id: str, project_id: str
    ) -> Project | None: ...

    async def find_plan(self, account_id: str, plan_id: str) -> Plan | None: ...

    async def create_plan(self, account_id: str, project_id: str) -> Plan: ...

    async def find_furniture(self, description: str) -> Furniture: ...
