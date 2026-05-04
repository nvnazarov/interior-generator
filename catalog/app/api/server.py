from typing import Annotated

import uvicorn
from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel

from app.core.models import Furniture
from app.core.service import MAX_LIMIT, FurnitureNotFoundError, Service


class SearchResult(BaseModel):
    class Meta(BaseModel):
        cursor: str | None = None

    furniture: list[Furniture]
    meta: Meta


class Server(FastAPI):
    def __init__(self, service: Service):
        super().__init__(
            title="Catalog API",
            summary="Furniture catalog",
        )

        @self.get("/furniture/{furniture_id}")
        async def get_furniture_by_id(furniture_id: str) -> Furniture:
            try:
                return await service.get_furniture_by_id(furniture_id)
            except FurnitureNotFoundError:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "furniture not found")

        @self.get("/search")
        async def search_furniture(
            cursor: Annotated[str | None, Query(max_length=256)] = None,
            area: Annotated[Furniture.Area | None, Query(max_length=32)] = None,
            name: Annotated[str | None, Query(max_length=64)] = None,
            limit: Annotated[int, Query(le=MAX_LIMIT)] = MAX_LIMIT,
        ) -> SearchResult:
            if cursor is None:
                furniture, next_cursor = await service.search_furniture(
                    name, area, limit
                )
            else:
                (
                    furniture,
                    next_cursor,
                ) = await service.get_next_search_result(cursor, limit)
            return SearchResult(
                furniture=furniture, meta=SearchResult.Meta(cursor=next_cursor)
            )

        @self.get("/search/description")
        async def find_furniture_by_description(
            description: Annotated[str, Query(max_length=512)],
            limit: Annotated[int, Query(le=MAX_LIMIT)] = MAX_LIMIT,
        ) -> list[Furniture]:
            return await service.find_furniture_by_description(description, limit)

        @self.get("/health", status_code=204)
        async def health():
            pass

    def listen_and_serve(self, host: str = "127.0.0.1", port: int = 8080):
        uvicorn.run(self, host=host, port=port, log_config=None)
