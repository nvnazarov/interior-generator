import base64
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ValidationError
from sqlalchemy import Row, String, bindparam, text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.catalog import IFurnitureRepository
from app.core.errors import InvalidCursorError
from app.core.models import Cursor, Furniture, SearchResult


class PostgresCursor(BaseModel):
    last_id: UUID
    area: str | None = None
    name: str | None = None


def encode_cursor(cursor: PostgresCursor) -> Cursor:
    return base64.b64encode(cursor.model_dump_json().encode("utf-8")).decode("utf-8")


def decode_cursor(cursor: Cursor) -> PostgresCursor:
    try:
        return PostgresCursor.model_validate_json(
            base64.b64decode(cursor).decode("utf-8")
        )
    except ValidationError:
        raise InvalidCursorError()


def parse_row(row: Row[Any]) -> Furniture:
    return Furniture(
        id=row[0],
        name=row[1],
        width=row[2],
        height=row[3],
        depth=row[4],
        mount=row[5],
        model_path=row[6],
        icon_path=row[7],
        thumbnail_path=row[8],
        meta=row[9],
    )


class PostgresFurnitureRepository(IFurnitureRepository):
    stmt_get = text(
        "SELECT "
        "   id, "
        "   name, "
        "   width, "
        "   height, "
        "   depth, "
        "   mount, "
        "   model_path, "
        "   icon_path, "
        "   thumbnail_path, "
        "   meta "
        "FROM catalog.catalog "
        "WHERE id = :furniture_id"
    )
    stmt_search = text(
        "SELECT "
        "   id, "
        "   name, "
        "   width, "
        "   height, "
        "   depth, "
        "   mount, "
        "   model_path, "
        "   icon_path, "
        "   thumbnail_path, "
        "   meta "
        "FROM catalog.catalog "
        "WHERE "
        "   (:name IS NULL OR name ILIKE '%' || :name || '%') "
        "   AND (:area IS NULL OR meta ->> 'area' = :area) "
        "ORDER BY id "
        "LIMIT :limit"
    ).bindparams(
        bindparam("name", type_=String),
        bindparam("area", type_=String),
    )
    stmt_search_with_cursor = text(
        "SELECT "
        "   id, "
        "   name, "
        "   width, "
        "   height, "
        "   depth, "
        "   mount, "
        "   model_path, "
        "   icon_path, "
        "   thumbnail_path, "
        "   meta "
        "FROM catalog.catalog "
        "WHERE "
        "   (:name IS NULL OR name ILIKE '%' || :name || '%') "
        "   AND (:area IS NULL OR meta ->> 'area' = :area) "
        "   AND id > :last_id "
        "ORDER BY id "
        "LIMIT :limit"
    ).bindparams(
        bindparam("name", type_=String),
        bindparam("area", type_=String),
    )

    def __init__(self, engine: AsyncEngine):
        self.engine = engine

    async def search_with_cursor(self, cursor: Cursor, limit: int) -> SearchResult:
        pg_cursor = decode_cursor(cursor)
        async with self.engine.connect() as c:
            result = await c.execute(
                self.stmt_search_with_cursor,
                {
                    "last_id": pg_cursor.last_id,
                    "area": pg_cursor.area,
                    "name": pg_cursor.name,
                    "limit": limit,
                },
            )
            furniture = [parse_row(row) for row in result.all()]
            next_cursor = (
                None
                if len(furniture) == 0
                else encode_cursor(
                    PostgresCursor(
                        last_id=furniture[-1].id,
                        name=pg_cursor.name,
                        area=pg_cursor.area,
                    )
                )
            )
            return furniture, next_cursor

    async def search(
        self, name: str | None, area: Furniture.Area | None, limit: int
    ) -> SearchResult:
        async with self.engine.connect() as c:
            result = await c.execute(
                self.stmt_search,
                {
                    "name": name,
                    "area": area,
                    "limit": limit,
                },
            )
            furniture = [parse_row(row) for row in result.all()]
            cursor = (
                None
                if len(furniture) == 0
                else encode_cursor(
                    PostgresCursor(last_id=furniture[-1].id, name=name, area=area)
                )
            )
            return furniture, cursor

    async def get(self, furniture_id: UUID) -> Furniture | None:
        async with self.engine.connect() as c:
            result = await c.execute(
                self.stmt_get,
                {"furniture_id": furniture_id},
            )
            if (row := result.one_or_none()) is None:
                return None
            else:
                return parse_row(row)

    async def get_top_k_like(self, k: int, description: str) -> list[Furniture]:
        return []
