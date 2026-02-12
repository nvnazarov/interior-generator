from typing import Annotated
from uuid import UUID

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


class API:
    def __init__(self, catalog: Catalog):
        self.catalog = catalog

    def asgi(self) -> FastAPI:
        app = FastAPI(
            title="Catalog API", summary="Furniture & other interior elements catalog"
        )

        @app.get("/furniture/{furniture_id}")
        async def get_furniture_by_id(furniture_id: UUID) -> Furniture:
            try:
                return await self.catalog.get_furniture_by_id(furniture_id)
            except FurnitureNotFoundError:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "furniture not found")

        @app.get("/search")
        async def search_furniture(
            cursor: Annotated[str | None, Query(max_length=256)] = None,
            area: Annotated[Furniture.Area | None, Query(max_length=32)] = None,
            name: Annotated[str | None, Query(max_length=64)] = None,
            limit: Annotated[int, Query(le=MAX_LIMIT)] = MAX_LIMIT,
        ) -> SearchResult:
            try:
                if cursor is None:
                    furniture, next_cursor = await self.catalog.search_furniture(
                        name, area, limit
                    )
                else:
                    furniture, next_cursor = (
                        await self.catalog.search_furniture_with_cursor(cursor, limit)
                    )
            except InvalidCursorError:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "invalid cursor")
            return SearchResult(
                furniture=furniture, meta=SearchResult.Meta(cursor=next_cursor)
            )

        return app

    def serve_http(self, host: str = "127.0.0.1", port: int = 8080):
        import uvicorn

        uvicorn.run(self.asgi(), host=host, port=port)
