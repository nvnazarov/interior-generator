import logging
from typing import Annotated
from uuid import UUID

import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException, Response, status
from fastapi.responses import PlainTextResponse

from app.api.errors import (
    HTTPPlanNotFound,
    HTTPPlansLimitExceeded,
    HTTPProjectNotFound,
    HTTPProjectsLimitExceeded,
)
from app.api.schema.plan import Patch as PlanPatch
from app.api.schema.plan import Plan as PlanSchema
from app.api.schema.project import Patch as ProjectPatch
from app.api.schema.project import Project as ProjectSchema
from app.core.account import ProjectsLimitExceeded
from app.core.plan import PatchError as PlanPatchError
from app.core.plan import Plan
from app.core.plan import RevisionError as PlanRevisionError
from app.core.project import PatchError as ProjectPatchError
from app.core.project import PlansLimitExceededError, Project
from app.core.project import RevisionError as ProjectRevisionError
from app.core.service import PlanNotFoundError, ProjectNotFoundError, Service

logger = logging.getLogger(__name__)

DEFAULT_HEADER = "x-account-id"


def attach_project_etag(response: Response, project: Project) -> None:
    response.headers["ETag"] = f"project-{project.id.hex}-{project.revision}"


def parse_project_etag(etag: str) -> int:
    return int(etag.split("-")[-1])


def attach_plan_etag(response: Response, plan: Plan) -> None:
    response.headers["ETag"] = get_plan_etag(plan)


def parse_plan_etag(etag: str) -> int:
    if not etag.startswith("plan-"):
        raise ValueError
    revision = int(etag[5:])
    if revision == 0 and len(etag) > 6:
        raise ValueError
    return revision


def get_plan_etag(plan: Plan):
    return f"plan-{plan.revision}"


class ASGI(FastAPI):
    def __init__(
        self,
        service: Service,
        *,
        header_for_account_id: str = DEFAULT_HEADER,
    ):
        self.service = service
        self.header_for_account_id = header_for_account_id

        super().__init__(
            title="Projects",
            summary="Manage projects and plans",
        )

        def get_account_id(
            account_id: Annotated[
                str,
                Header(alias=self.header_for_account_id),
            ] = "",
        ) -> str:
            if account_id == "":
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
            return account_id

        @self.post("/projects", status_code=status.HTTP_201_CREATED, tags=["projects"])
        async def create_project(
            response: Response,
            account_id: Annotated[str, Depends(get_account_id)],
        ) -> ProjectSchema:
            try:
                project = await self.service.create_project(account_id)
                attach_project_etag(response, project)
                return ProjectSchema.from_core(project)
            except ProjectsLimitExceeded:
                raise HTTPProjectsLimitExceeded

        @self.get("/projects/{project_id}", tags=["projects"])
        async def get_project(
            response: Response,
            project_id: UUID,
            account_id: Annotated[str, Depends(get_account_id)],
            revision: Annotated[str | None, Header(alias="if-none-match")] = None,
        ):
            try:
                project = await self.service.get_project(account_id, project_id)
                if revision is not None and project.revision == parse_project_etag(
                    revision
                ):
                    return PlainTextResponse("", status.HTTP_304_NOT_MODIFIED)
                attach_project_etag(response, project)
                return ProjectSchema.from_core(project)
            except ProjectNotFoundError:
                raise HTTPProjectNotFound

        @self.post(
            "/projects/{project_id}/publish",
            status_code=status.HTTP_204_NO_CONTENT,
            tags=["projects"],
        )
        async def publish_project(
            project_id: UUID, account_id: Annotated[str, Depends(get_account_id)]
        ) -> None:
            try:
                await self.service.publish_project(project_id, account_id)
            except ProjectNotFoundError:
                raise HTTPProjectNotFound

        @self.post(
            "/projects/{project_id}/unpublish",
            status_code=status.HTTP_204_NO_CONTENT,
            tags=["projects"],
        )
        async def unpublish_project(
            project_id: UUID, account_id: Annotated[str, Depends(get_account_id)]
        ) -> None:
            try:
                await self.service.unublish_project(project_id, account_id)
            except ProjectNotFoundError:
                raise HTTPProjectNotFound

        @self.delete(
            "/projects/{project_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            tags=["projects"],
        )
        async def delete_project(
            project_id: UUID, account_id: Annotated[str, Depends(get_account_id)]
        ) -> None:
            try:
                await self.service.delete_project(account_id, project_id)
            except ProjectNotFoundError:
                raise HTTPProjectNotFound

        @self.patch(
            "/projects/{project_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            tags=["projects"],
        )
        async def patch_project(
            response: Response,
            project_id: UUID,
            account_id: Annotated[str, Depends(get_account_id)],
            patch: ProjectPatch,
            revision: Annotated[str, Header(alias="if-match")],
        ) -> None:
            try:
                project = await self.service.patch_project(
                    account_id,
                    project_id,
                    patch=patch.to_core(),
                    revision=parse_project_etag(revision),
                )
                attach_project_etag(response, project)
            except ProjectNotFoundError:
                raise HTTPProjectNotFound
            except ProjectPatchError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="invalid patch",
                )
            except ProjectRevisionError:
                raise HTTPException(
                    status.HTTP_412_PRECONDITION_FAILED, detail="incorrect revision"
                )

        @self.get("/projects", tags=["projects"], response_model_exclude_none=True)
        async def get_projects_owned_by_account(
            account_id: Annotated[str, Depends(get_account_id)],
        ) -> list[ProjectSchema]:
            projects = await self.service.get_projects_owned_by_account(account_id)
            return list(map(ProjectSchema.from_core, projects))

        @self.post(
            "/projects/{project_id}/plans",
            tags=["plans"],
            status_code=status.HTTP_201_CREATED,
        )
        async def create_plan(
            response: Response,
            project_id: UUID,
            account_id: Annotated[str, Depends(get_account_id)],
        ) -> PlanSchema:
            try:
                plan = await self.service.create_plan(account_id, project_id)
                attach_plan_etag(response, plan)
                return PlanSchema.from_core(plan)
            except PlansLimitExceededError:
                raise HTTPPlansLimitExceeded
            except ProjectNotFoundError:
                raise HTTPProjectNotFound

        @self.get("/plans/{plan_id}", tags=["plans"])
        async def get_plan(
            response: Response,
            plan_id: UUID,
            account_id: Annotated[str, Depends(get_account_id)],
            etag: Annotated[str | None, Header(alias="if-none-match")] = None,
        ):
            try:
                plan = await self.service.get_plan(account_id, plan_id)
                if etag is not None and etag == get_plan_etag(plan):
                    return PlainTextResponse("", status.HTTP_304_NOT_MODIFIED)
                attach_plan_etag(response, plan)
                return PlanSchema.from_core(plan)
            except PlanNotFoundError:
                raise HTTPPlanNotFound

        @self.get(
            "/projects/{project_id}/plans",
            tags=["plans"],
            response_model_exclude_none=True,
        )
        async def get_plans_of_project(
            project_id: UUID,
            account_id: Annotated[str, Depends(get_account_id)],
        ) -> list[PlanSchema]:
            try:
                plans = await self.service.get_plans_of_project(account_id, project_id)
                return list(map(PlanSchema.from_core, plans))
            except ProjectNotFoundError:
                raise HTTPProjectNotFound

        @self.delete(
            "/plans/{plan_id}",
            tags=["plans"],
            status_code=status.HTTP_204_NO_CONTENT,
        )
        async def delete_plan(
            plan_id: UUID, account_id: Annotated[str, Depends(get_account_id)]
        ):
            try:
                await self.service.delete_plan(account_id, plan_id)
            except PlanNotFoundError:
                raise HTTPPlanNotFound

        @self.patch(
            "/plans/{plan_id}",
            tags=["plans"],
            status_code=status.HTTP_204_NO_CONTENT,
        )
        async def patch_plan(
            response: Response,
            plan_id: UUID,
            account_id: Annotated[str, Depends(get_account_id)],
            patch: PlanPatch,
            etag: Annotated[str, Header(alias="if-match")],
        ) -> None:
            try:
                plan = await self.service.patch_plan(
                    account_id,
                    plan_id,
                    patch=patch.to_core(),
                    revision=parse_plan_etag(etag),
                )
                attach_plan_etag(response, plan)
            except PlanNotFoundError:
                raise HTTPPlanNotFound
            except PlanPatchError as e:
                logger.error({"msg": "plan patch error", "error": str(e)})
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="invalid patch",
                )
            except PlanRevisionError:
                raise HTTPException(
                    status.HTTP_412_PRECONDITION_FAILED, detail="incorrect revision"
                )

        @self.get("/health", status_code=204)
        async def healthcheck():
            pass

    def listen_and_serve(self, host: str = "127.0.0.1", port: int = 8080):
        uvicorn.run(self, host=host, port=port, log_config=None)
