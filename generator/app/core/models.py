from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field
from uuid import uuid4

from app.utils.datetime import current_time


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

        walls: dict[str, Wall] = Field(default_factory=dict)
        doors: dict[str, Door] = Field(default_factory=dict)
        windows: dict[str, Window] = Field(default_factory=dict)
        wet_areas: dict[str, WetArea] = Field(default_factory=dict)

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

        furniture: dict[str, Furniture] = Field(default_factory=dict)
        areas: dict[str, Area] = Field(default_factory=dict)

    class Patch(BaseModel):
        class Content(BaseModel):
            class Furniture(BaseModel):
                furniture_id: str | None = None
                x: int | None = None
                y: int | None = None
                z: int | None = None
                yaw: float | None = None

            class Area(BaseModel):
                class Point(BaseModel):
                    x: int
                    y: int

                type: str | None = None
                points: list[Point] | None = None

            furniture: dict[str, Furniture | None] = Field(default_factory=dict)
            areas: dict[str, Area | None] = Field(default_factory=dict)

        name: str | None = None
        content: Content = Field(default_factory=Content)

    id: str
    project_id: str
    content: Content = Field(default_factory=Content)
    name: str = Field("", max_length=256)
    revision: int


class Prompt(BaseModel):
    id: str
    project_id: str
    base: Plan.Content | None
    text: str
    patches: list[Plan.Patch]
    dt_created: datetime
    dt_done: datetime | None
    status: Literal["pending", "success", "failed"]

    @staticmethod
    def create(project_id: str, text: str, base: Plan.Content | None) -> "Prompt":
        return Prompt(
            id=uuid4().hex,
            project_id=project_id,
            base=base,
            text=text,
            patches=[],
            dt_created=current_time(),
            dt_done=None,
            status="pending",
        )

    def success(self, patches: list[Plan.Patch]):
        self.status = "success"
        self.dt_done = current_time()
        self.patches = patches

    def fail(self):
        self.status = "failed"
        self.dt_done = current_time()


class Furniture(BaseModel):
    id: str
    name: str
    width: int
    height: int
    depth: int
    mount: Literal["floor", "wall", "ceiling"]
