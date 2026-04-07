import asyncio
from uuid import UUID

from app.adapters.elastic import ElasticFurnitureRepository
from app.configs.root import RootConfig
from app.core.models import Furniture


def seed_elastic():
    config = RootConfig()
    repository = ElasticFurnitureRepository(config.elastic.host, config.elastic.index)
    asyncio.run(
        repository.save_bulk(
            [
                # Bedroom.
                (
                    Furniture(
                        id=UUID("ca5c064d-1aa8-4c2b-9bfe-5371511a81e7"),
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
                        id=UUID("c6467d46-d63b-4540-b511-a880c1dae100"),
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
                        id=UUID("2a614c19-a95b-4e01-b0e4-b431349431cd"),
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
                        id=UUID("b666929e-a35d-4430-a480-64d5687851c6"),
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
                        id=UUID("fcf71f9b-c746-4326-af08-f75ce4b53205"),
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
                        id=UUID("c6526f02-d725-4c2d-9df1-0702cfd1c120"),
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
                        id=UUID("3e1a6fbc-5936-4a77-b60d-2242de89a533"),
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
                    "Fridge",
                ),
                (
                    Furniture(
                        id=UUID("909e3d2f-7962-491d-9b15-6cf505b45373"),
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
                        id=UUID("a0008fe6-8d7a-4e87-bea3-ee1b6c534a2e"),
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
                    "Oven",
                ),
                (
                    Furniture(
                        id=UUID("2327dfcc-f736-48f3-b854-267001c5e985"),
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
                        id=UUID("3403b538-ba3b-46c2-8fce-bfabaa2de9c8"),
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
                        id=UUID("ec072a85-a929-4a71-aec0-af7f3f5364ab"),
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
                        id=UUID("46769d3b-aa9d-4dc6-b3ac-918c9d8e51aa"),
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
                        id=UUID("a7a3d620-d5db-4e7d-9a8e-3e4e22a81a42"),
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
                        id=UUID("e8565c3d-7c4b-49cb-a31b-d716fb73e0c2"),
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
            ]
        )
    )


if __name__ == "__main__":
    seed_elastic()
