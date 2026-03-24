from typing import Annotated
from uuid import UUID

import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException

from app.core.server import Server


class ASGI(FastAPI):
    def __init__(self, server: Server, header_for_account_id: str = "x-account-id"):
        super().__init__(
            title="Generator",
            summary="Generates plans based on instructions provided by user",
        )

        def get_account_id(
            account_id: Annotated[
                str,
                Header(alias=header_for_account_id),
            ] = "",
        ) -> UUID:
            try:
                return UUID(account_id)
            except ValueError:
                raise HTTPException(status_code=401)

        @self.post("/projects/{project_id}/plans/generate")
        async def generate_plans(
            project_id: UUID,
            account_id: Annotated[UUID, Depends(get_account_id)],
            base_plan_id: UUID | None = None,
            n: int = 5,
        ) -> list[UUID]:
            plans = await server.generate_plans(account_id, project_id, base_plan_id, n)
            return [plan.id for plan in plans]

        @self.get("/health", status_code=204)
        async def healthcheck():
            pass

    def listen_and_serve(self, host: str = "127.0.0.1", port: int = 8080):
        uvicorn.run(self, host=host, port=port, log_config=None)
