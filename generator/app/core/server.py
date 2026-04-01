from uuid import UUID

from app.core.plan import Plan

DEFAULT_PLANS_COUNT = 5


class Server:
    def __init__(self):
        pass

    async def generate_plans(
        self,
        account_id: str,
        project_id: UUID,
        base_plan_id: UUID | None = None,
        n: int = DEFAULT_PLANS_COUNT,
    ) -> list[Plan]:
        return [Plan.empty(project_id)]
