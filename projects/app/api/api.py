from typing import Annotated
from uuid import UUID

from fastapi import Body, Depends, FastAPI, Header, HTTPException, status

from app.api.idempotency import IdempotencyProvider
from app.api.views import plan as plan_views
from app.api.views import project as project_views
from app.api.views import shell as shell_views
from app.core.plan.errors import (
    PlanNotFoundError,
    PlanPatchError,
    PlansPerProjectLimitExceededError,
    PlanVersionConflictError,
)
from app.core.plan.service import PlanService
from app.core.project.errors import (
    ProjectNotFoundError,
    ProjectsPerAccountLimitExceededError,
)
from app.core.project.service import ProjectService
from app.core.shell.errors import (
    ShellNotFoundError,
    ShellPatchError,
    ShellsPerAccountLimitExceededError,
    ShellVersionConflictError,
)
from app.core.shell.service import ShellService


class API:
    def __init__(
        self,
        plan_service: PlanService,
        shell_service: ShellService,
        project_service: ProjectService,
        idempotency_provider: IdempotencyProvider,
        header_with_account_id: str,
    ):
        self.plan_service = plan_service
        self.shell_service = shell_service
        self.project_service = project_service
        self.header_with_account_id = header_with_account_id
        self.make_idempotent = idempotency_provider.make_idempotent

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

        @app.post("/projects", status_code=status.HTTP_201_CREATED, tags=["projects"])
        @self.make_idempotent
        async def create_project(
            account_id: Annotated[UUID, Depends(get_account_id)],
        ) -> project_views.Project:
            try:
                project = await self.project_service.create_project(account_id)
                return project_views.Project.from_model(project)
            except ProjectsPerAccountLimitExceededError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="projects limit exceeded",
                )

        @app.get("/projects", tags=["projects"])
        async def get_all_projects(
            account_id: Annotated[UUID, Depends(get_account_id)],
        ) -> list[project_views.Project]:
            projects = await self.project_service.get_all_projects(account_id)
            return list(map(project_views.Project.from_model, projects))

        @app.get("/projects/{project_id}", tags=["projects"])
        async def get_project_by_id(
            project_id: UUID, account_id: Annotated[UUID, Depends(get_account_id)]
        ) -> project_views.Project:
            project = await self.project_service.get_project_by_id(
                account_id, project_id
            )
            if project is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
            return project_views.Project.from_model(project)

        @app.delete(
            "/projects/{project_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            tags=["projects"],
        )
        async def delete_project(
            project_id: UUID, account_id: Annotated[UUID, Depends(get_account_id)]
        ) -> None:
            await self.project_service.delete_project(account_id, project_id)

        @app.patch(
            "/projects/{project_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            tags=["projects"],
        )
        @self.make_idempotent
        async def patch_project(
            project_id: UUID,
            account_id: Annotated[UUID, Depends(get_account_id)],
            patch: project_views.Patch,
        ) -> None:
            try:
                kwargs = patch.model_dump(exclude_none=True)
                await self.project_service.patch_project(
                    account_id, project_id, **kwargs
                )
            except ProjectNotFoundError:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        @app.post(
            "/projects/{project_id}/pin",
            status_code=status.HTTP_204_NO_CONTENT,
            tags=["projects"],
        )
        async def pin_project(
            project_id: UUID, account_id: Annotated[UUID, Depends(get_account_id)]
        ) -> None:
            try:
                await self.project_service.pin_project(account_id, project_id)
            except ProjectNotFoundError:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        @app.post(
            "/projects/{project_id}/unpin",
            status_code=status.HTTP_204_NO_CONTENT,
            tags=["projects"],
        )
        async def unpin_project(
            project_id: UUID, account_id: Annotated[UUID, Depends(get_account_id)]
        ) -> None:
            try:
                await self.project_service.unpin_project(account_id, project_id)
            except ProjectNotFoundError:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        @app.post("/shells", status_code=status.HTTP_201_CREATED, tags=["shells"])
        async def create_shell(
            account_id: Annotated[UUID, Depends(get_account_id)],
        ) -> shell_views.Shell:
            try:
                shell = await self.shell_service.create_shell(account_id)
                return shell_views.Shell.from_model(shell)
            except ShellsPerAccountLimitExceededError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="shells limit exceeded",
                )

        @app.get("/shells", tags=["shells"])
        async def get_all_shells(
            account_id: Annotated[UUID, Depends(get_account_id)],
        ) -> list[shell_views.ShellNoContent]:
            shells = await self.shell_service.get_all_shells(account_id)
            return list(map(shell_views.ShellNoContent.from_model, shells))

        @app.get("/shells/{shell_id}", tags=["shells"])
        async def get_shell_by_id(
            shell_id: UUID,
            account_id: Annotated[UUID, Depends(get_account_id)],
        ) -> shell_views.Shell:
            shell = await self.shell_service.get_shell_by_id(account_id, shell_id)
            if shell is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
            return shell_views.Shell.from_model(shell)

        @app.delete(
            "/shells/{shell_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            tags=["shells"],
        )
        async def delete_shell(
            shell_id: UUID, account_id: Annotated[UUID, Depends(get_account_id)]
        ) -> None:
            await self.shell_service.delete_shell(account_id, shell_id)

        @app.patch(
            "/shells/{shell_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            tags=["shells"],
        )
        async def patch_shell(
            shell_id: UUID,
            account_id: Annotated[UUID, Depends(get_account_id)],
            name: Annotated[str, Body(embed=True)],
        ) -> None:
            try:
                await self.shell_service.rename_shell(account_id, shell_id, name)
            except ShellNotFoundError:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        @app.patch("/shells/{shell_id}/content", tags=["shells"])
        async def patch_shell_content(
            shell_id: UUID,
            account_id: Annotated[UUID, Depends(get_account_id)],
            patch: shell_views.Patch,
        ) -> int:
            try:
                version = await self.shell_service.patch_shell(
                    account_id, shell_id, patch.to_model()
                )
                return version
            except ShellNotFoundError:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
            except ShellVersionConflictError:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, detail="version conflict"
                )
            except ShellPatchError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="failed to apply the patch",
                )

        @app.post("/projects/{project_id}/plans", status_code=status.HTTP_201_CREATED)
        async def create_plan(
            project_id: UUID,
            shell_id: UUID,
            account_id: Annotated[UUID, Depends(get_account_id)],
        ) -> plan_views.Plan:
            try:
                plan = await self.plan_service.create_plan(
                    account_id, project_id, shell_id
                )
                return plan_views.Plan.from_model(plan)
            except PlansPerProjectLimitExceededError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="plans limit exceeded",
                )
            except ProjectNotFoundError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="project not found"
                )

        @app.get("/projects/{project_id}/plans")
        async def get_all_project_plans(
            project_id: UUID,
            account_id: Annotated[UUID, Depends(get_account_id)],
        ) -> list[plan_views.PlanNoContent]:
            plans = await self.plan_service.get_all_project_plans(
                account_id, project_id
            )
            return list(map(plan_views.PlanNoContent.from_model, plans))

        @app.get("/plans/{plan_id}")
        async def get_plan_by_id(
            plan_id: UUID,
            account_id: Annotated[UUID, Depends(get_account_id)],
        ) -> plan_views.Plan:
            plan = await self.plan_service.get_plan_by_id(account_id, plan_id)
            if plan is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
            return plan_views.Plan.from_model(plan)

        @app.delete("/plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
        async def delete_plan(
            plan_id: UUID, account_id: Annotated[UUID, Depends(get_account_id)]
        ):
            await self.plan_service.delete_plan(account_id, plan_id)

        @app.patch("/plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
        async def patch_plan(
            plan_id: UUID,
            account_id: Annotated[UUID, Depends(get_account_id)],
            name: Annotated[str, Body(embed=True)],
        ) -> None:
            await self.plan_service.rename_plan(account_id, plan_id, name)

        @app.patch("/plans/{plan_id}/content")
        async def patch_plan_content(
            plan_id: UUID,
            account_id: Annotated[UUID, Depends(get_account_id)],
            patch: plan_views.Patch,
        ) -> int:
            try:
                version = await self.plan_service.patch_plan(
                    account_id, plan_id, patch.to_model()
                )
                return version
            except PlanNotFoundError:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
            except PlanVersionConflictError:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT)
            except PlanPatchError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="failed to apply the patch",
                )

        return app

    def serve_http(self, host: str = "127.0.0.1", port: int = 8080):
        import uvicorn

        uvicorn.run(self.asgi(), host=host, port=port)

        uvicorn.run(self.asgi(), host=host, port=port)

        uvicorn.run(self.asgi(), host=host, port=port)
