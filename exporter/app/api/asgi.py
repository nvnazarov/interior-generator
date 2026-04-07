from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.responses import StreamingResponse

from app.api.constants import MIME_DXF, MIME_PDF
from app.api.schema import DXFExportOptions, PDFExportOptions
from app.core.exporter import Exporter, PlanNotFoundError, ProjectNotFoundError

DEFAULT_HEADER_FOR_ACCOUNT_ID = "x-account-id"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8080


class ASGI(FastAPI):
    def __init__(
        self,
        exporter: Exporter,
        *,
        header_for_account_id: str = DEFAULT_HEADER_FOR_ACCOUNT_ID,
    ):
        self.exporter = exporter

        super().__init__(
            title="Exporter",
            summary="Exports projects and plans into various formats",
        )

        def get_account_id(
            account_id: Annotated[
                str,
                Header(alias=header_for_account_id),
            ] = "",
        ) -> str:
            if account_id == "":
                raise HTTPException(status.HTTP_401_UNAUTHORIZED)
            return account_id

        @self.post("/projects/{project_id}/export/pdf")
        async def export_project_pdf(
            project_id: str,
            account_id: Annotated[str, Depends(get_account_id)],
            opts: PDFExportOptions,
        ):
            try:
                buffer = await self.exporter.export_project_pdf(project_id, account_id)
            except ProjectNotFoundError:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND, detail={"project not found"}
                )
            else:
                return StreamingResponse(
                    buffer,
                    media_type=MIME_PDF,
                    headers={
                        "Content-Disposition": f"attachment; filename=project-{project_id}.pdf"
                    },
                )

        @self.post("/plans/{plan_id}/export/dxf")
        async def export_plan_dxf(
            plan_id: str,
            account_id: Annotated[str, Depends(get_account_id)],
            opts: DXFExportOptions,
        ):
            try:
                buffer = await self.exporter.export_plan_dxf(plan_id, account_id)
            except PlanNotFoundError:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND, detail={"plan not found"}
                )
            else:
                return StreamingResponse(
                    buffer,
                    media_type=MIME_DXF,
                    headers={
                        "Content-Disposition": f"attachment; filename=plans-{plan_id}.dxf"
                    },
                )

        @self.get("/health", status_code=204)
        async def healthcheck():
            pass

    def listen_and_serve(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        uvicorn.run(self, host=host, port=port, log_config=None)
