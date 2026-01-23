from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI
from fastapi.responses import StreamingResponse

from app.api.schema import DXFExportOptions, PDFExportOptions
from app.core.exporter import Exporter


class API:
    def __init__(self, exporter: Exporter):
        self.exporter = exporter

    def asgi(self) -> FastAPI:
        app = FastAPI()

        def get_account_id():
            pass

        @app.post("/export/{project_id}/pdf")
        async def export_project_pdf(
            project_id: UUID,
            account_id: Annotated[UUID, Depends(get_account_id)],
            opts: PDFExportOptions,
        ):
            buffer = await self.exporter.export_pdf(project_id, account_id)
            return StreamingResponse(
                buffer,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename=project-{project_id.hex}.pdf"
                },
            )

        @app.post("/export/{project_id}/dxf")
        async def export_project_dxf(
            project_id: UUID,
            account_id: Annotated[UUID, Depends(get_account_id)],
            opts: DXFExportOptions,
        ):
            buffer = await self.exporter.export_dxf(project_id, account_id)
            return StreamingResponse(
                buffer,
                media_type="application/dxf",
                headers={
                    "Content-Disposition": f"attachment; filename=project-{project_id.hex}.dxf"
                },
            )

        return app

    def run(self, host: str = "127.0.0.1", port: int = 8080):
        import uvicorn

        app = self.asgi()
        uvicorn.run(app, host=host, port=port)
