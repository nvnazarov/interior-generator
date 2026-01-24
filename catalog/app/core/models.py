from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class Furniture(BaseModel):
    class Area(str, Enum):
        KITCHEN = "kitchen"
        LIVING_ROOM = "living_room"
        BATHROOM = "bathroom"
        BEDROOM = "bedroom"

    class Function(str, Enum):
        DINING = ""
        STORAGE = "storage"
        SLEEP = "sleep"
        RELAX = "relax"

    class Meta(BaseModel):
        area: "Furniture.Area | None" = None
        function: "Furniture.Function | None" = None

    class Mount(str, Enum):
        FLOOR = "floor"
        CEILING = "ceiling"
        WALL = "wall"

    id: UUID
    name: str
    width: int = Field(ge=0)
    height: int = Field(ge=0)
    depth: int = Field(ge=0)
    mount: Mount
    model_path: str
    icon_path: str
    thumbnail_path: str
    meta: Meta


Cursor = str
SearchResult = tuple[list[Furniture], Cursor | None]
