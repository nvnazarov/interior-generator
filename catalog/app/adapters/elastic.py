import base64
import logging
from typing import Any

from elasticsearch import AsyncElasticsearch, NotFoundError
from elasticsearch.helpers import async_bulk
from pydantic import BaseModel, ValidationError

from app.core.catalog import Catalog
from app.core.models import Cursor, Furniture, SearchResult

logger = logging.getLogger(__name__)


class ElasticCursor(BaseModel):
    area: str | None = None
    name: str | None = None
    sort: list[Any] | None = None


def encode_cursor(cursor: ElasticCursor) -> Cursor:
    return base64.b64encode(cursor.model_dump_json().encode("utf-8")).decode("utf-8")


def decode_cursor(cursor: Cursor) -> ElasticCursor:
    try:
        return ElasticCursor.model_validate_json(
            base64.b64decode(cursor).decode("utf-8")
        )
    except ValidationError:
        raise RuntimeError("invalid cursor")


def furniture_to_elastic(furniture: Furniture) -> dict[str, Any]:
    return {
        "_id": furniture.id,
        "_source": {
            "id": furniture.id,
            "name": furniture.name,
            "width": furniture.width,
            "height": furniture.height,
            "depth": furniture.depth,
            "mount": furniture.mount.value,
            "model_path": furniture.model_path,
            "icon_path": furniture.icon_path,
            "thumbnail_path": furniture.thumbnail_path,
            "meta": {
                "area": furniture.meta.area.value if furniture.meta.area else None,
            },
        },
    }


def elastic_to_furniture(doc: dict[str, Any]) -> Furniture:
    source = doc["_source"]
    return Furniture(
        id=source["id"],
        name=source["name"],
        width=source["width"],
        height=source["height"],
        depth=source["depth"],
        mount=Furniture.Mount(source["mount"]),
        model_path=source["model_path"],
        icon_path=source["icon_path"],
        thumbnail_path=source["thumbnail_path"],
        meta=Furniture.Meta(
            area=(
                Furniture.Area(source["meta"]["area"])
                if source["meta"].get("area")
                else None
            ),
        ),
    )


class ElasticCatalog(Catalog):
    def __init__(self, host: str, index: str = "catalog"):
        self._index = index
        self._host = host

    async def get_next_search_result(self, cursor: Cursor, limit: int) -> SearchResult:
        es_cursor = decode_cursor(cursor)
        must: list[Any] = []
        if es_cursor.name:
            must.append(
                {"match": {"name": {"query": es_cursor.name, "operator": "and"}}}
            )
        if es_cursor.area:
            must.append({"term": {"meta.area": es_cursor.area}})
        body: dict[str, Any] = {
            "query": {"bool": {"must": must if must else [{"match_all": {}}]}},
            "sort": [{"id": "asc"}],
            "size": limit,
        }
        if es_cursor.sort:
            body["search_after"] = es_cursor.sort
        async with AsyncElasticsearch(hosts=[self._host]) as es:
            result = await es.search(index=self._index, body=body)
        furniture = [elastic_to_furniture(hit) for hit in result["hits"]["hits"]]
        next_cursor = None
        if furniture and len(furniture) == limit:
            last_hit = result["hits"]["hits"][-1]
            next_cursor = encode_cursor(
                ElasticCursor(
                    name=es_cursor.name,
                    area=es_cursor.area,
                    sort=last_hit["sort"],
                )
            )
        return furniture, next_cursor

    async def search(
        self, name: str | None, area: Furniture.Area | None, limit: int
    ) -> SearchResult:
        must: list[Any] = []
        if name:
            must.append({"match": {"name": {"query": name, "operator": "and"}}})
        if area:
            must.append({"term": {"meta.area": area.value}})
        body: dict[str, Any] = {
            "query": {"bool": {"must": must if must else [{"match_all": {}}]}},
            "sort": [{"id": "asc"}],
            "size": limit,
        }
        async with AsyncElasticsearch(hosts=[self._host]) as es:
            result = await es.search(index=self._index, body=body)
        furniture_list = [elastic_to_furniture(hit) for hit in result["hits"]["hits"]]
        cursor = None
        if furniture_list and len(furniture_list) == limit:
            last_hit = result["hits"]["hits"][-1]
            cursor = encode_cursor(
                ElasticCursor(
                    name=name,
                    area=area.value if area else None,
                    sort=last_hit["sort"],
                )
            )
        return furniture_list, cursor

    async def find(self, furniture_id: str) -> Furniture | None:
        async with AsyncElasticsearch(hosts=[self._host]) as es:
            try:
                result = await es.get(index=self._index, id=furniture_id)
            except NotFoundError:
                return None
            else:
                return elastic_to_furniture(result.raw)

    async def find_by_description(
        self, description: str, limit: int
    ) -> list[Furniture]:
        should: list[Any] = []
        if description:
            should.extend(
                [
                    {
                        "match": {
                            "description": {
                                "query": description,
                                "boost": 2.0,
                                "analyzer": "english",
                            }
                        }
                    },
                    {
                        "match": {
                            "name": {
                                "query": description,
                                "boost": 1.5,
                                "fuzziness": "AUTO",
                            }
                        }
                    },
                    {
                        "match_phrase": {
                            "description": {
                                "query": description,
                                "boost": 3.0,
                                "slop": 2,
                            }
                        }
                    },
                ]
            )
        body: dict[str, Any] = {
            "query": {
                "bool": {
                    "should": should,
                }
            },
            "size": limit,
        }
        async with AsyncElasticsearch(hosts=[self._host]) as es:
            result = await es.search(index=self._index, body=body)
        furniture: list[Furniture] = []
        for hit in result["hits"]["hits"]:
            f = elastic_to_furniture(hit)
            furniture.append(f)
        return furniture

    async def save_bulk(
        self,
        furniture_list: list[tuple[Furniture, str | None]],
    ) -> None:
        actions: list[Any] = []
        for furniture, description in furniture_list:
            doc: dict[str, Any] = {
                "id": furniture.id,
                "name": furniture.name,
                "width": furniture.width,
                "height": furniture.height,
                "depth": furniture.depth,
                "mount": furniture.mount.value,
                "model_path": furniture.model_path,
                "icon_path": furniture.icon_path,
                "thumbnail_path": furniture.thumbnail_path,
                "meta": {
                    "area": furniture.meta.area.value if furniture.meta.area else None,
                },
            }
            if description:
                doc["description"] = description
            actions.append({"_index": self._index, "_id": furniture.id, "_source": doc})
        if actions:
            async with AsyncElasticsearch(hosts=[self._host]) as es:
                _, failed = await async_bulk(client=es, actions=actions, refresh=True)
                if failed:
                    raise Exception("failed to index some furniture")

    async def ensure_index_exists(self) -> None:
        async with AsyncElasticsearch(hosts=[self._host]) as es:
            if not await es.indices.exists(index=self._index):
                mappings: dict[str, Any] = {
                    "mappings": {
                        "properties": {
                            "id": {"type": "keyword"},
                            "name": {
                                "type": "text",
                                "fields": {
                                    "keyword": {"type": "keyword"},
                                    "lowercase": {
                                        "type": "text",
                                        "analyzer": "lowercase",
                                    },
                                },
                            },
                            # This field allows to search furniture in the catalog
                            # by semantic meaning. It is not exposed in the model.
                            "description": {
                                "type": "text",
                                "analyzer": "standard",
                                "fields": {
                                    "english": {"type": "text", "analyzer": "english"},
                                },
                            },
                            "width": {"type": "integer"},
                            "height": {"type": "integer"},
                            "depth": {"type": "integer"},
                            "mount": {"type": "keyword"},
                            "model_path": {"type": "keyword"},
                            "icon_path": {"type": "keyword"},
                            "thumbnail_path": {"type": "keyword"},
                            "meta": {
                                "properties": {
                                    "area": {"type": "keyword"},
                                }
                            },
                        }
                    },
                    "settings": {
                        "analysis": {
                            "analyzer": {
                                "lowercase": {
                                    "type": "custom",
                                    "tokenizer": "keyword",
                                    "filter": ["lowercase"],
                                }
                            }
                        }
                    },
                }
                await es.indices.create(index=self._index, body=mappings)
