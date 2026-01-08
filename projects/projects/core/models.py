from typing import Any
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class Shell(BaseModel):
    id: UUID
    name: str = Field(max_length=256)
    data: Any


class Project(BaseModel):
    id: UUID
    account_id: UUID
    name: str = Field(max_length=256)
    description: str = Field(max_length=2048)
    pinned: bool
    created_at: datetime
    updated_at: datetime


class PublishedProject(Project):
    url: str
    published_at: datetime


class Plan(BaseModel):
    id: UUID
    project_id: UUID
    name: str = Field(max_length=256)
    created_at: datetime
    updated_at: datetime


class Location(BaseModel):
    x: int
    y: int
    z: int
