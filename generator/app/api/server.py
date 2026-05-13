from typing import Annotated

import uvicorn
from fastapi import Body, Depends, FastAPI, Header, HTTPException

from app.core.models import Prompt
from app.core.service import PromptNotFoundError, Service


class Server(FastAPI):
    def __init__(self, service: Service, account_header: str = "x-account-id"):
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
        async def create_prompt(
            project_id: str,
            account_id: Annotated[str, Depends(get_account_id)],
            text: Annotated[str, Body()],
            base_plan_id: Annotated[str | None, Body()] = None,
            count: Annotated[int, Body()] = 5,
        ) -> Prompt:
            prompt = await service.create_prompt(
                account_id=account_id,
                project_id=project_id,
                text=text,
                base_plan_id=base_plan_id,
                count=count,
            )
            return prompt

        @self.get("/projects/{project_id}/prompts", response_model_exclude_unset=True)
        async def get_prompts_in_project(
            project_id: str, account_id: Annotated[str, Depends(get_account_id)]
        ) -> list[Prompt]:
            prompts = await service.get_prompts_in_project(
                account_id=account_id, project_id=project_id
            )
            return prompts

        @self.delete("/prompts/{prompt_id}", status_code=204)
        async def delete_prompt(
            prompt_id: str, account_id: Annotated[str, Depends(get_account_id)]
        ):
            try:
                await service.delete_prompt(account_id=account_id, prompt_id=prompt_id)
            except PromptNotFoundError:
                raise HTTPException(status_code=404, detail="prompt not found")

        @self.get("/health", status_code=204)
        async def health():
            pass

    def listen_and_serve(self, host: str = "127.0.0.1", port: int = 8080):
        uvicorn.run(self, host=host, port=port, log_config=None)
