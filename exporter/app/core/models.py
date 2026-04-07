from enum import Enum

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
    walls: dict[str, Wall] = Field(default_factory=dict)
    doors: dict[str, Door] = Field(default_factory=dict)
    windows: dict[str, Window] = Field(default_factory=dict)
    wet_areas: dict[str, WetArea] = Field(default_factory=dict)


class Project(BaseModel):
    id: str
    name: str
    content: ProjectContent


class PlanContent(BaseModel):
    furniture: dict[str, FurnitureInPlan] = Field(default_factory=dict)
    areas: dict[str, Area] = Field(default_factory=dict)


class Plan(BaseModel):
    id: str
    project_id: str
    name: str
    content: PlanContent
