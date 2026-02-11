from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.responses import StreamingResponse

from app.api.constants import MIME_DXF, MIME_PDF
from app.api.schema import DXFExportOptions, PDFExportOptions
from app.core.exporter import Exporter

DEFAULT_HEADER = "x-account-id"


class ASGI(FastAPI):
    def __init__(
        self,
        exporter: Exporter,
        *,
        header_for_account_id: str = DEFAULT_HEADER,
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
        ) -> UUID:
            try:
                return UUID(account_id)
            except ValueError:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        @self.post("/export/{project_id}/pdf")
        async def export_project_pdf(
            project_id: UUID,
            account_id: Annotated[UUID, Depends(get_account_id)],
            opts: PDFExportOptions,
        ):
            buffer = await self.exporter.export_pdf(project_id, account_id)
            return StreamingResponse(
                buffer,
                media_type=MIME_PDF,
                headers={
                    "Content-Disposition": f"attachment; filename=project-{project_id.hex}.pdf"
                },
            )

        @self.post("/export/{project_id}/dxf")
        async def export_project_dxf(
            project_id: UUID,
            account_id: Annotated[UUID, Depends(get_account_id)],
            opts: DXFExportOptions,
        ):
            buffer = await self.exporter.export_dxf(project_id, account_id)
            return StreamingResponse(
                buffer,
                media_type=MIME_DXF,
                headers={
                    "Content-Disposition": f"attachment; filename=project-{project_id.hex}.dxf"
                },
            )

    def run(self, host: str = "127.0.0.1", port: int = 8080):
        import uvicorn

        uvicorn.run(self, host=host, port=port)
