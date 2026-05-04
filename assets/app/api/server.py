import logging

import uvicorn
from fastapi import FastAPI, HTTPException, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.constants import MAX_AVATAR_SIZE_BYTES
from app.core.service import AvatarSizeTooBigError, Service

logger = logging.getLogger(__name__)


class Server(FastAPI):
    def __init__(self, service: Service):
        super().__init__(
            title="Assets API",
            summary="Manage assets",
        )

        @self.post("/avatars")
        async def create_avatar(file: UploadFile) -> str:
            if file.content_type not in ["image/jpeg", "image/jpg", "image/png"]:
                raise HTTPException(
                    400, "only jpeg, jpg, and png avatars are supported"
                )
            data = await file.read(MAX_AVATAR_SIZE_BYTES + 1)
            try:
                avatar_id = await service.create_avatar(data)
            except AvatarSizeTooBigError:
                raise HTTPException(413, "file is too big")
            else:
                return avatar_id

        @self.get("/health", status_code=204)
        async def health():
            pass

        @self.exception_handler(RequestValidationError)
        async def handle_req_validation_error(
            request: Request, exc: RequestValidationError
        ):
            logger.error(exc)
            return JSONResponse(
                status_code=422,
                content={"detail": exc.errors()},
            )

    def listen_and_serve(self, host: str = "127.0.0.1", port: int = 8080):
        uvicorn.run(self, host=host, port=port, log_config=None)
