import asyncio

from app.adapters.elastic import ElasticCatalog
from app.configs.root import RootConfig
from app.core.models import Furniture


def seed_elastic():
    config = RootConfig()
    elastic = ElasticCatalog(config.elastic.host, config.elastic.index)
    asyncio.run(
        elastic.save_bulk(
            [
                # Bedroom.
                (
                    Furniture(
                        id="bed",
                        name="Bed",
                        width=200,
                        height=60,
                        depth=100,
                        mount=Furniture.Mount.FLOOR,
                        model_path="",
                        icon_path="",
                        thumbnail_path="",
                        meta=Furniture.Meta(area=Furniture.Area.BEDROOM),
                    ),
                    "A bed for one person",
                ),
                (
                    Furniture(
                        id="double-bed",
                        name="Double Bed",
                        width=200,
                        height=60,
                        depth=200,
                        mount=Furniture.Mount.FLOOR,
                        model_path="",
                        icon_path="",
                        thumbnail_path="",
                        meta=Furniture.Meta(area=Furniture.Area.BEDROOM),
                    ),
                    "A bed for two persons",
                ),
                # Bathroom.
                (
                    Furniture(
                        id="toilet",
                        name="Toilet",
                        width=40,
                        height=110,
                        depth=40,
                        mount=Furniture.Mount.FLOOR,
                        model_path="",
                        icon_path="",
                        thumbnail_path="",
                        meta=Furniture.Meta(area=Furniture.Area.BATHROOM),
                    ),
                    "Toilet",
                ),
                (
                    Furniture(
                        id="bathtub",
                        name="Bathtub",
                        width=150,
                        height=60,
                        depth=60,
                        mount=Furniture.Mount.FLOOR,
                        model_path="",
                        icon_path="",
                        thumbnail_path="",
                        meta=Furniture.Meta(area=Furniture.Area.BATHROOM),
                    ),
                    "Bathtub",
                ),
                (
                    Furniture(
                        id="shower-cabin",
                        name="Shower Cabin",
                        width=80,
                        height=200,
                        depth=80,
                        mount=Furniture.Mount.FLOOR,
                        model_path="",
                        icon_path="",
                        thumbnail_path="",
                        meta=Furniture.Meta(area=Furniture.Area.BATHROOM),
                    ),
                    "Shower cabin",
                ),
                (
                    Furniture(
                        id="bathroom-sink",
                        name="Bathroom Sink",
                        width=100,
                        height=130,
                        depth=40,
                        mount=Furniture.Mount.FLOOR,
                        model_path="",
                        icon_path="",
                        thumbnail_path="",
                        meta=Furniture.Meta(area=Furniture.Area.BATHROOM),
                    ),
                    "Bathroom Sink",
                ),
                # Kitchen.
                (
                    Furniture(
                        id="fridge",
                        name="Fridge",
                        width=60,
                        height=200,
                        depth=60,
                        mount=Furniture.Mount.FLOOR,
                        model_path="",
                        icon_path="",
                        thumbnail_path="",
                        meta=Furniture.Meta(area=Furniture.Area.KITCHEN),
                    ),
                    "Fridge, refrigerator",
                ),
                (
                    Furniture(
                        id="dishwasher",
                        name="Dishwasher",
                        width=60,
                        height=80,
                        depth=60,
                        mount=Furniture.Mount.FLOOR,
                        model_path="",
                        icon_path="",
                        thumbnail_path="",
                        meta=Furniture.Meta(area=Furniture.Area.KITCHEN),
                    ),
                    "Dishwasher",
                ),
                (
                    Furniture(
                        id="oven",
                        name="Oven",
                        width=60,
                        height=80,
                        depth=60,
                        mount=Furniture.Mount.FLOOR,
                        model_path="",
                        icon_path="",
                        thumbnail_path="",
                        meta=Furniture.Meta(area=Furniture.Area.KITCHEN),
                    ),
                    "Oven, stove",
                ),
                (
                    Furniture(
                        id="cupboard",
                        name="Cupboard",
                        width=60,
                        height=100,
                        depth=60,
                        mount=Furniture.Mount.WALL,
                        model_path="",
                        icon_path="",
                        thumbnail_path="",
                        meta=Furniture.Meta(area=Furniture.Area.KITCHEN),
                    ),
                    "Cupboard",
                ),
                (
                    Furniture(
                        id="kitchen-table",
                        name="Kitchen Table",
                        width=110,
                        height=80,
                        depth=60,
                        mount=Furniture.Mount.FLOOR,
                        model_path="",
                        icon_path="",
                        thumbnail_path="",
                        meta=Furniture.Meta(area=Furniture.Area.KITCHEN),
                    ),
                    "Kitchen table",
                ),
                # Living room.
                (
                    Furniture(
                        id="sofa",
                        name="Sofa",
                        width=200,
                        height=80,
                        depth=80,
                        mount=Furniture.Mount.FLOOR,
                        model_path="",
                        icon_path="",
                        thumbnail_path="",
                        meta=Furniture.Meta(area=Furniture.Area.LIVING_ROOM),
                    ),
                    "Sofa",
                ),
                (
                    Furniture(
                        id="coffee-table",
                        name="Coffee Table",
                        width=100,
                        height=50,
                        depth=100,
                        mount=Furniture.Mount.FLOOR,
                        model_path="",
                        icon_path="",
                        thumbnail_path="",
                        meta=Furniture.Meta(area=Furniture.Area.LIVING_ROOM),
                    ),
                    "Coffee Table",
                ),
                (
                    Furniture(
                        id="lamp",
                        name="Lamp",
                        width=30,
                        height=150,
                        depth=30,
                        mount=Furniture.Mount.FLOOR,
                        model_path="",
                        icon_path="",
                        thumbnail_path="",
                        meta=Furniture.Meta(area=Furniture.Area.LIVING_ROOM),
                    ),
                    "Lamp",
                ),
                # Miscellaneous.
                (
                    Furniture(
                        id="chair",
                        name="Chair",
                        width=40,
                        height=100,
                        depth=40,
                        mount=Furniture.Mount.FLOOR,
                        model_path="",
                        icon_path="",
                        thumbnail_path="",
                        meta=Furniture.Meta(),
                    ),
                    "Chair, stool, office chair, kitchen chair",
                ),
                (
                    Furniture(
                        id="flower",
                        name="Flower",
                        width=30,
                        height=40,
                        depth=30,
                        mount=Furniture.Mount.SURFACE,
                        model_path="",
                        icon_path="",
                        thumbnail_path="",
                        meta=Furniture.Meta(),
                    ),
                    "Flower, plant",
                ),
            ]
        )
    )


if __name__ == "__main__":
    seed_elastic()
