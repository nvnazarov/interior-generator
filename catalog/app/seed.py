import asyncio
from uuid import UUID

from app.configs.root import RootConfig
from app.adapters.elastic import ElasticFurnitureRepository
from app.core.models import Furniture


def seed_elastic():
    config = RootConfig()
    repository = ElasticFurnitureRepository(config.elastic.host, config.elastic.index)
    asyncio.run(
        repository.save_bulk(
            [
                (
                    Furniture(
                        id=UUID("6709e439-1bf2-4ebd-9b47-0f55d34560b0"),
                        name="Chair",
                        width=40,
                        height=120,
                        depth=40,
                        mount=Furniture.Mount.FLOOR,
                        model_path="",
                        icon_path="",
                        thumbnail_path="",
                        meta=Furniture.Meta(area=Furniture.Area.LIVING_ROOM),
                    ),
                    "Chair, stool, office chair, kitchen chair",
                ),
                (
                    Furniture(
                        id=UUID("5b6f2cdb-0b3e-4137-854c-68113fca968f"),
                        name="Bed",
                        width=200,
                        height=50,
                        depth=100,
                        mount=Furniture.Mount.FLOOR,
                        model_path="",
                        icon_path="",
                        thumbnail_path="",
                        meta=Furniture.Meta(area=Furniture.Area.BEDROOM),
                    ),
                    "Bed",
                ),
                (
                    Furniture(
                        id=UUID("0c8cff3b-9148-40a2-8451-c02fa4ccd12b"),
                        name="Cupboard",
                        width=40,
                        height=120,
                        depth=40,
                        mount=Furniture.Mount.WALL,
                        model_path="",
                        icon_path="",
                        thumbnail_path="",
                        meta=Furniture.Meta(area=Furniture.Area.KITCHEN),
                    ),
                    "Cupboard",
                ),
            ]
        )
    )


if __name__ == "__main__":
    seed_elastic()
