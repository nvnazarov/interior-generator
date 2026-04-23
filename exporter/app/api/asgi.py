from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.responses import StreamingResponse

from app.core.exporter import Exporter, ProjectNotFoundError


class ASGI(FastAPI):
    def __init__(
        self,
        exporter: Exporter,
        *,
        header_for_account_id: str = "x-account-id",
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
                    media_type="application/pdf",
                    headers={
                        "Content-Disposition": f"attachment; filename=project-{project_id}.pdf"
                    },
                )

        @self.get("/health", status_code=204)
        async def healthcheck():
            pass

    def listen_and_serve(self, host: str = "127.0.0.1", port: int = 8080):
        uvicorn.run(self, host=host, port=port, log_config=None)
