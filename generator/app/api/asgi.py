from typing import Annotated

import uvicorn
from fastapi import Body, Depends, FastAPI, Header, HTTPException

from app.core.models import Prompt
from app.core.server import PromptNotFoundError, Server


class ASGI(FastAPI):
    def __init__(self, server: Server, account_header: str = "x-account-id"):
        super().__init__(
            title="Generator",
            summary="Generates plans based on instructions provided by user",
        )

        def get_account_id(
            account_id: Annotated[
                str,
                Header(alias=account_header),
            ] = "",
        ) -> str:
            if account_id == "":
                raise HTTPException(status_code=401)
            return account_id

        @self.post("/projects/{project_id}/prompts", response_model_exclude_unset=True)
        async def generate_plans(
            project_id: str,
            account_id: Annotated[str, Depends(get_account_id)],
            text: Annotated[str, Body()],
            base_plan_id: Annotated[str | None, Body()] = None,
            count: Annotated[int, Body()] = 5,
        ) -> Prompt:
            prompt = await server.generate_plans(
                account_id, project_id, text, base_plan_id, count
            )
            return prompt

        @self.get("/projects/{project_id}/prompts", response_model_exclude_unset=True)
        async def get_prompts_for_project(
            project_id: str, account_id: Annotated[str, Depends(get_account_id)]
        ) -> list[Prompt]:
            return await server.get_prompts_for_project(account_id, project_id)

        @self.delete("/prompts/{prompt_id}", status_code=204)
        async def delete_prompt(
            prompt_id: str,
            account_id: Annotated[str, Depends(get_account_id)],
        ):
            try:
                await server.delete_prompt(account_id, prompt_id)
            except PromptNotFoundError:
                raise HTTPException(status_code=404, detail="prompt not found")

        @self.get("/health", status_code=204)
        async def healthcheck():
            pass

    def listen_and_serve(self, host: str = "127.0.0.1", port: int = 8080):
        uvicorn.run(self, host=host, port=port, log_config=None)
