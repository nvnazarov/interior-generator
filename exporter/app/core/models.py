from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class AreaType(str, Enum):
    KITCHEN = "kitchen"
    BEDROOM = "bedroom"
    BATHROOM = "bathroom"
    LIVINGROOM = "livingroom"
    HALLWAY = "hallway"


class Furniture(BaseModel):
    name: str
    x: float
    y: float
    z: float
    width: float
    height: float
    depth: float
    yaw: float


class FurnitureInPlan(BaseModel):
    id: str
    furniture_id: str
    x: int
    y: int
    z: int
    yaw: float


class Point(BaseModel):
    x: int
    y: int


class WetArea(BaseModel):
    id: str
    points: list[Point]


class Area(BaseModel):
    id: str
    type: AreaType
    points: list[Point]


class Wall(BaseModel):
    id: str
    x1: int
    y1: int
    x2: int
    y2: int


class Door(BaseModel):
    id: str
    wall_id: str
    x: int = Field(ge=0)
    w: int = Field(ge=0)
    h: int = Field(ge=0)


class Window(BaseModel):
    id: str
    wall_id: str
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    w: int = Field(ge=0)
    h: int = Field(ge=0)


class ProjectContent(BaseModel):
    walls: dict[str, Wall] = {}
    doors: dict[str, Door] = {}
    windows: dict[str, Window] = {}
    wet_areas: dict[str, WetArea] = {}


class Project(BaseModel):
    id: UUID
    name: str
    content: ProjectContent


class PlanContent(BaseModel):
    furniture: dict[str, FurnitureInPlan] = {}
    areas: dict[str, Area] = {}


class Plan(BaseModel):
    id: UUID
    project_id: UUID
    name: str
    content: PlanContent
