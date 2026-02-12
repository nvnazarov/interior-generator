from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class AreaType(str, Enum):
    KITCHEN = "kitchen"
    BEDROOM = "bedroom"
    BATHROOM = "bathroom"
    LIVINGROOM = "livingroom"


class Furniture(BaseModel):
    name: str
    x: float
    y: float
    z: float
    width: float
    height: float
    depth: float
    yaw: float


class WetArea(BaseModel):
    id: UUID
    x: int
    y: int
    w: int = Field(ge=0)
    h: int = Field(ge=0)


class Area(BaseModel):
    type: AreaType
    x: float
    y: float
    w: float = Field(ge=0)
    h: float = Field(ge=0)


class Wall(BaseModel):
    id: UUID
    x1: int
    y1: int
    x2: int
    y2: int

    @model_validator(mode="after")
    def validate_wall_is_parallel_to_axes(self) -> "Wall":
        if self.x1 != self.x2 and self.y1 != self.y2:
            raise ValueError("wall is not parallel to axes")
        return self


class Door(BaseModel):
    id: UUID
    wall_id: UUID
    x: int = Field(ge=0)
    w: int = Field(ge=0)
    h: int = Field(ge=0)


class Window(BaseModel):
    id: UUID
    wall_id: UUID
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    w: int = Field(ge=0)
    h: int = Field(ge=0)


class ProjectContent(BaseModel):
    walls: dict[UUID, Wall] = {}
    doors: dict[UUID, Door] = {}
    windows: dict[UUID, Window] = {}
    wet_areas: dict[UUID, WetArea] = {}


class Project(BaseModel):
    id: UUID
    name: str
    content: ProjectContent


class PlanContent(BaseModel):
    furniture: dict[UUID, Furniture] = {}
    areas: dict[UUID, Area] = {}


class Plan(BaseModel):
    id: UUID
    project_id: UUID
    name: str
    content: PlanContent

    # def translate(self, dx: float, dy: float):
    #     for area in self.areas:
    #         area.x += dx
    #         area.y += dy
    #     for wall in self.walls.values():
    #         wall.x1 += dx
    #         wall.x2 += dx
    #         wall.y1 += dy
    #         wall.y2 += dy
    #     for furniture in self.furniture:
    #         furniture.x += dx
    #         furniture.y += dy

    # def scale(self, scale: float):
    #     for area in self.areas:
    #         area.x *= scale
    #         area.y *= scale
    #         area.w *= scale
    #         area.h *= scale
    #     for wall in self.walls.values():
    #         wall.x1 *= scale
    #         wall.x2 *= scale
    #         wall.y1 *= scale
    #         wall.y2 *= scale
    #     for furniture in self.furniture:
    #         furniture.x *= scale
    #         furniture.y *= scale
    #         furniture.width *= scale
    #         furniture.height *= scale

    # def boundary(self) -> Vec4:
    #     if len(self.areas) == len(self.walls) == 0:
    #         return Vec4(0, 0, 0, 0)

    #     min_x, max_x, min_y, max_y = 1e5, -1e5, 1e5, -1e5
    #     for obj in self.areas:
    #         min_x = min(min_x, obj.x)
    #         min_y = min(min_y, obj.y)
    #         max_x = max(max_x, obj.x + obj.w)
    #         max_y = max(max_y, obj.y + obj.h)
    #     for obj in self.walls.values():
    #         min_x = min(min_x, obj.x1, obj.x2)
    #         min_y = min(min_y, obj.y1, obj.y2)
    #         max_x = max(max_x, obj.x1, obj.x2)
    #         max_y = max(max_y, obj.y1, obj.y2)
    #     for obj in self.furniture:
    #         # TODO: furniture should be inside walls boundary,
    #         # but we actually cannot know it beforehand.
    #         pass

    #     return Vec4(min_x, min_y, max_x - min_x, max_y - min_y)
