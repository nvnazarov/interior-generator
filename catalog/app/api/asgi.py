from typing import Annotated
from uuid import UUID

import uvicorn
from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel

from app.core.catalog import MAX_LIMIT, Catalog
from app.core.errors import FurnitureNotFoundError, InvalidCursorError
from app.core.models import Furniture


class SearchResult(BaseModel):
    class Meta(BaseModel):
        cursor: str | None = None

    furniture: list[Furniture]
    meta: Meta


class ASGI(FastAPI):
    def __init__(self, catalog: Catalog):
        super().__init__(
            title="Catalog API",
            summary="Furniture & other interior elements catalog",
        )

        @self.get("/furniture/{furniture_id}")
        async def get_furniture_by_id(furniture_id: UUID) -> Furniture:
            try:
                return await catalog.get_furniture_by_id(furniture_id)
            except FurnitureNotFoundError:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "furniture not found")

        @self.get("/search")
        async def search_furniture(
            cursor: Annotated[str | None, Query(max_length=256)] = None,
            area: Annotated[Furniture.Area | None, Query(max_length=32)] = None,
            name: Annotated[str | None, Query(max_length=64)] = None,
            limit: Annotated[int, Query(le=MAX_LIMIT)] = MAX_LIMIT,
        ) -> SearchResult:
            try:
                if cursor is None:
                    furniture, next_cursor = await catalog.search_furniture(
                        name, area, limit
                    )
                else:
                    (
                        furniture,
                        next_cursor,
                    ) = await catalog.search_furniture_with_cursor(cursor, limit)
            except InvalidCursorError:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "invalid cursor")
            return SearchResult(
                furniture=furniture, meta=SearchResult.Meta(cursor=next_cursor)
            )

    def listen_and_serve(self, host: str = "127.0.0.1", port: int = 8080):
        uvicorn.run(self, host=host, port=port, log_config=None)
