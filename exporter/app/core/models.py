from enum import Enum
from typing import NamedTuple
from uuid import UUID

from pydantic import BaseModel, Field


class Vec4(NamedTuple):
    x: float
    y: float
    w: float
    h: float


class AreaType(str, Enum):
    KITCHEN = "kitchen"
    BEDROOM = "bedroom"
    BATHROOM = "bathroom"
    LIVINGROOM = "livingroom"
    WET_AREA = "wet_area"


class Furniture(BaseModel):
    name: str
    x: float
    y: float
    z: float
    width: float
    height: float
    depth: float
    yaw: float


class Area(BaseModel):
    type: AreaType
    x: float
    y: float
    w: float
    h: float

    def area_sqm(self) -> float:
        return self.w * self.h


class Wall(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class Door(BaseModel):
    wall_id: UUID
    x: float = Field(ge=0)
    w: float = Field(ge=0)
    h: float = Field(ge=0)


class Window(BaseModel):
    wall_id: UUID
    x: float = Field(ge=0)
    y: float = Field(ge=0)
    w: float = Field(ge=0)
    h: float = Field(ge=0)


class Plan(BaseModel):
    name: str
    furniture: list[Furniture] = []
    areas: list[Area] = []
    walls: dict[UUID, Wall] = {}
    windows: list[Window] = []
    doors: list[Door] = []

    def translate(self, dx: float, dy: float):
        for area in self.areas:
            area.x += dx
            area.y += dy
        for wall in self.walls.values():
            wall.x1 += dx
            wall.x2 += dx
            wall.y1 += dy
            wall.y2 += dy
        for furniture in self.furniture:
            furniture.x += dx
            furniture.y += dy

    def scale(self, scale: float):
        for area in self.areas:
            area.x *= scale
            area.y *= scale
            area.w *= scale
            area.h *= scale
        for wall in self.walls.values():
            wall.x1 *= scale
            wall.x2 *= scale
            wall.y1 *= scale
            wall.y2 *= scale
        for furniture in self.furniture:
            furniture.x *= scale
            furniture.y *= scale
            furniture.width *= scale
            furniture.height *= scale

    def boundary(self) -> Vec4:
        if len(self.areas) == len(self.walls) == 0:
            return Vec4(0, 0, 0, 0)

        min_x, max_x, min_y, max_y = 1e5, -1e5, 1e5, -1e5
        for obj in self.areas:
            min_x = min(min_x, obj.x)
            min_y = min(min_y, obj.y)
            max_x = max(max_x, obj.x + obj.w)
            max_y = max(max_y, obj.y + obj.h)
        for obj in self.walls.values():
            min_x = min(min_x, obj.x1, obj.x2)
            min_y = min(min_y, obj.y1, obj.y2)
            max_x = max(max_x, obj.x1, obj.x2)
            max_y = max(max_y, obj.y1, obj.y2)
        for obj in self.furniture:
            # TODO: furniture should be inside walls boundary,
            # but we actually cannot know it beforehand.
            pass

        return Vec4(min_x, min_y, max_x - min_x, max_y - min_y)
