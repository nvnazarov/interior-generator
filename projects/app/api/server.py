import logging
from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException, Response, status
from fastapi.responses import PlainTextResponse

from app.api.errors import (
    HTTPPlanNotFound,
    HTTPPlansLimitExceeded,
    HTTPProjectNotFound,
    HTTPProjectsLimitExceeded,
)
from app.core.account import ProjectsLimitExceededError
from app.core.plan import Plan, PlanPatchError, PlanRevisionError
from app.core.project import (
    PlansLimitExceededError,
    Project,
    ProjectPatchError,
    ProjectRevisionError,
)
from app.core.service import (
    AccessDeniedError,
    PlanNotFoundError,
    ProjectNotFoundError,
    Service,
)

logger = logging.getLogger(__name__)


def get_project_etag(project: Project) -> str:
    return f"project-{hash(project)}"


def attach_project_etag(response: Response, project: Project) -> None:
    response.headers["ETag"] = get_project_etag(project)


def attach_plan_etag(response: Response, plan: Plan) -> None:
    response.headers["ETag"] = get_plan_etag(plan)


def get_plan_etag(plan: Plan):
    return f"plan-{hash(plan)}"


class Server(FastAPI):
    def __init__(
        self,
        service: Service,
        *,
        account_header: str,
    ):
        self._service = service
        self._account_header = account_header

        super().__init__(
            title="Projects",
            summary="Manage projects and plans",
        )

        def get_account_id(
            account_id: Annotated[
                str,
                Header(alias=self._account_header),
            ] = "",
        ) -> str:
            if account_id == "":
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
            return account_id

        @self.post("/projects", status_code=status.HTTP_201_CREATED, tags=["projects"])
        async def create_project(
            response: Response,
            account_id: Annotated[str, Depends(get_account_id)],
        ) -> Project:
            try:
                project = await self._service.create_project(account_id)
                attach_project_etag(response, project)
                return project
            except ProjectsLimitExceededError:
                raise HTTPProjectsLimitExceeded

        @self.get("/projects/{project_id}", tags=["projects"])
        async def get_project(
            response: Response,
            project_id: str,
            account_id: Annotated[str, Depends(get_account_id)],
            etag: Annotated[str | None, Header(alias="if-none-match")] = None,
        ):
            try:
                project = await self._service.get_project(account_id, project_id)
                if etag and etag == get_project_etag(project):
                    return PlainTextResponse("", status.HTTP_304_NOT_MODIFIED)
                attach_project_etag(response, project)
                return project
            except (ProjectNotFoundError, AccessDeniedError):
                raise HTTPProjectNotFound

        @self.post("/projects/{project_id}/publish", tags=["projects"])
        async def publish_project(
            project_id: str, account_id: Annotated[str, Depends(get_account_id)]
        ) -> Project:
            try:
                project = await self._service.publish_project(project_id, account_id)
                return project
            except (ProjectNotFoundError, AccessDeniedError):
                raise HTTPProjectNotFound

        @self.post("/projects/{project_id}/unpublish", tags=["projects"])
        async def unpublish_project(
            project_id: str, account_id: Annotated[str, Depends(get_account_id)]
        ) -> Project:
            try:
                project = await self._service.unublish_project(project_id, account_id)
                return project
            except (ProjectNotFoundError, AccessDeniedError):
                raise HTTPProjectNotFound

        @self.delete(
            "/projects/{project_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            tags=["projects"],
        )
        async def delete_project(
            project_id: str, account_id: Annotated[str, Depends(get_account_id)]
        ) -> None:
            try:
                await self._service.delete_project(account_id, project_id)
            except (ProjectNotFoundError, AccessDeniedError):
                raise HTTPProjectNotFound

        @self.patch(
            "/projects/{project_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            tags=["projects"],
        )
        async def patch_project(
            response: Response,
            project_id: str,
            account_id: Annotated[str, Depends(get_account_id)],
            patch: Project.Patch,
            revision: Annotated[int, Header(alias="if-match")],
        ) -> None:
            try:
                project = await self._service.patch_project(
                    account_id,
                    project_id,
                    patch=patch,
                    revision=revision,
                )
                response.headers["ETag"] = str(project.revision)
            except (ProjectNotFoundError, AccessDeniedError):
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

        @self.get("/projects", tags=["projects"])
        async def get_projects_owned_by_account(
            account_id: Annotated[str, Depends(get_account_id)],
        ) -> list[Project]:
            projects = await self._service.get_projects_owned_by_account(account_id)
            return projects

        @self.post(
            "/projects/{project_id}/plans",
            tags=["plans"],
            status_code=status.HTTP_201_CREATED,
        )
        async def create_plan(
            response: Response,
            project_id: str,
            account_id: Annotated[str, Depends(get_account_id)],
        ) -> Plan:
            try:
                plan = await self._service.create_plan(account_id, project_id)
                attach_plan_etag(response, plan)
                return plan
            except PlansLimitExceededError:
                raise HTTPPlansLimitExceeded
            except (ProjectNotFoundError, AccessDeniedError):
                raise HTTPProjectNotFound

        @self.get("/plans/{plan_id}", tags=["plans"])
        async def get_plan(
            response: Response,
            plan_id: str,
            account_id: Annotated[str, Depends(get_account_id)],
            etag: Annotated[str | None, Header(alias="if-none-match")] = None,
        ):
            try:
                plan = await self._service.get_plan(account_id, plan_id)
                if etag and etag == get_plan_etag(plan):
                    return PlainTextResponse("", status.HTTP_304_NOT_MODIFIED)
                attach_plan_etag(response, plan)
                return plan
            except (PlanNotFoundError, AccessDeniedError):
                raise HTTPPlanNotFound

        @self.get(
            "/projects/{project_id}/plans",
            tags=["plans"],
            response_model_exclude_none=True,
        )
        async def get_plans_of_project(
            project_id: str,
            account_id: Annotated[str, Depends(get_account_id)],
        ) -> list[Plan]:
            try:
                plans = await self._service.get_plans_in_project(account_id, project_id)
                return plans
            except (ProjectNotFoundError, AccessDeniedError):
                raise HTTPProjectNotFound

        @self.delete(
            "/plans/{plan_id}",
            tags=["plans"],
            status_code=status.HTTP_204_NO_CONTENT,
        )
        async def delete_plan(
            plan_id: str, account_id: Annotated[str, Depends(get_account_id)]
        ):
            try:
                await self._service.delete_plan(account_id, plan_id)
            except (PlanNotFoundError, AccessDeniedError):
                raise HTTPPlanNotFound

        @self.patch(
            "/plans/{plan_id}",
            tags=["plans"],
            status_code=status.HTTP_204_NO_CONTENT,
        )
        async def patch_plan(
            response: Response,
            plan_id: str,
            account_id: Annotated[str, Depends(get_account_id)],
            patch: Plan.Patch,
            revision: Annotated[int, Header(alias="if-match")],
        ) -> None:
            try:
                plan = await self._service.patch_plan(
                    account_id,
                    plan_id,
                    patch=patch,
                    revision=revision,
                )
                response.headers["ETag"] = str(plan.revision)
            except (PlanNotFoundError, AccessDeniedError):
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
        async def health():
            pass

    def listen_and_serve(self, host: str = "127.0.0.1", port: int = 8080):
        uvicorn.run(self, host=host, port=port, log_config=None)
