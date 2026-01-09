from typing import Annotated
from uuid import UUID

from fastapi import FastAPI, HTTPException, Depends, status, Header

from projects.core.service import ProjectService
from projects.core.errors import (
    ProjectsPerAccountLimitExceededError,
    ProjectNotFoundError,
)
from projects.api.schema import Project, PatchProject


class API:
    def __init__(
        self,
        project_service: ProjectService,
        header_with_account_id: str,
    ):
        self.project_service = project_service
        self.header_with_account_id = header_with_account_id

    def asgi(self) -> FastAPI:
        app = FastAPI(title="Projects API", summary="Manage users' projects")

        def get_account_id(
            account_id: Annotated[
                str,
                Header(alias=self.header_with_account_id),
            ] = "",
        ) -> UUID:
            try:
                return UUID(account_id)
            except ValueError:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        @app.post("/projects", status_code=status.HTTP_201_CREATED)
        async def create_project(
            account_id: Annotated[UUID, Depends(get_account_id)],
        ) -> Project:
            try:
                project = await self.project_service.create_project(account_id)
                return Project.from_core(project)
            except ProjectsPerAccountLimitExceededError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        @app.get("/projects")
        async def get_all_projects(
            account_id: Annotated[UUID, Depends(get_account_id)],
        ) -> list[Project]:
            try:
                projects = await self.project_service.get_all_projects(account_id)
                return list(map(Project.from_core, projects))
            except ProjectsPerAccountLimitExceededError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Projects limit exceeded",
                )

        @app.get("/projects/{project_id}")
        async def get_project_by_id(
            project_id: UUID,
            account_id: Annotated[UUID, Depends(get_account_id)],
        ):
            project = await self.project_service.get_project_by_id(
                account_id, project_id
            )
            if project is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
            return Project.from_core(project)

        @app.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
        async def delete_project(
            project_id: UUID, account_id: Annotated[UUID, Depends(get_account_id)]
        ):
            await self.project_service.delete_project(account_id, project_id)

        @app.patch("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
        async def patch_project(
            project_id: UUID,
            account_id: Annotated[UUID, Depends(get_account_id)],
            patch: PatchProject,
        ):
            try:
                kwargs = patch.model_dump(exclude_none=True)
                await self.project_service.patch_project(
                    account_id, project_id, **kwargs
                )
            except ProjectNotFoundError:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        @app.post("/projects/{project_id}/pin", status_code=status.HTTP_204_NO_CONTENT)
        async def pin_project(
            project_id: UUID, account_id: Annotated[UUID, Depends(get_account_id)]
        ):
            try:
                await self.project_service.pin_project(account_id, project_id)
            except ProjectNotFoundError:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        @app.post(
            "/projects/{project_id}/unpin", status_code=status.HTTP_204_NO_CONTENT
        )
        async def unpin_project(
            project_id: UUID, account_id: Annotated[UUID, Depends(get_account_id)]
        ):
            try:
                await self.project_service.unpin_project(account_id, project_id)
            except ProjectNotFoundError:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        return app

    def serve_http(self, host: str = "127.0.0.1", port: int = 8080):
        import uvicorn

        uvicorn.run(self.asgi(), host=host, port=port)
