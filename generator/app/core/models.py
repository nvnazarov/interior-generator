from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Prompt(BaseModel):
    id: str
    project_id: str
    base_plan_id: str | None
    text: str
    generated_plans_ids: list[str]
    dt_created: datetime
    dt_done: datetime | None
    status: Literal["pending", "success", "failed"]


class Project(BaseModel):
    class Content(BaseModel):
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

        class Wall(BaseModel):
            id: str
            x1: int
            y1: int
            x2: int
            y2: int

        class WetArea(BaseModel):
            class Point(BaseModel):
                x: int
                y: int

            id: str
            points: list[Point]

        walls: dict[str, Wall] = {}
        doors: dict[str, Door] = {}
        windows: dict[str, Window] = {}
        wet_areas: dict[str, WetArea] = {}

    id: str
    account_id: str
    name: str = Field(max_length=256)
    description: str = Field(max_length=2048)
    content: Content = Field(default_factory=Content)


class Plan(BaseModel):
    class Content(BaseModel):
        class Furniture(BaseModel):
            id: str
            furniture_id: str
            x: int
            y: int
            z: int
            yaw: float

        class Area(BaseModel):
            class Point(BaseModel):
                x: int
                y: int

            id: str
            type: str
            points: list[Point]

        furniture: dict[str, Furniture] = {}
        areas: dict[str, Area] = {}

    id: str
    project_id: str
    content: Content = Field(default_factory=Content)
    name: str = Field("", max_length=256)


class Furniture(BaseModel):
    id: str
    name: str
    width: int
    height: int
    depth: int
    mount: Literal["floor", "wall", "ceiling"]
