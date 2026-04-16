import logging
from typing import Iterable
from abc import ABC, abstractmethod
from uuid import uuid4

from app.core.models import Furniture, Project, Plan

logger = logging.getLogger(__name__)


class Constraint(ABC):
    @abstractmethod
    def weights(self) -> dict[str, float]:
        """
        Get weights that this constraint adds to the objects
        that are constrained.
        """
        pass

    @abstractmethod
    def objects(self) -> list[str]:
        """Get objects that are constrained by this constraint."""
        pass


class OnFloor(Constraint):
    def __init__(self, object_id: str):
        self.object_id = object_id

    def weights(self) -> dict[str, float]:
        return {self.object_id: 1}

    def objects(self) -> list[str]:
        return [self.object_id]


class FarWall(Constraint):
    def __init__(self, object_id: str):
        self.object_id = object_id

    def weights(self) -> dict[str, float]:
        return {self.object_id: 1}

    def objects(self) -> list[str]:
        return [self.object_id]


class AgainstWall(Constraint):
    def __init__(self, object_id: str):
        self.object_id = object_id

    def weights(self) -> dict[str, float]:
        return {self.object_id: 2}

    def objects(self) -> list[str]:
        return [self.object_id]


class InFrontOf(Constraint):
    def __init__(self, a_object_id: str, b_object_id: str):
        self.a = a_object_id
        self.b = b_object_id

    def weights(self) -> dict[str, float]:
        return {self.a: 1, self.b: 1}

    def objects(self) -> list[str]:
        return [self.a, self.b]


class OnTopOf(Constraint):
    def __init__(self, bottom_object_id: str, top_object_id: str):
        self.bottom = bottom_object_id
        self.top = top_object_id

    def weights(self) -> dict[str, float]:
        return {self.bottom: 1, self.top: 0}

    def objects(self) -> list[str]:
        return [self.bottom, self.top]


class FaceToFace(Constraint):
    def __init__(self, a_object_id: str, b_object_id: str):
        self.a = a_object_id
        self.b = b_object_id

    def weights(self) -> dict[str, float]:
        return {self.a: 1, self.b: 1}

    def objects(self) -> list[str]:
        return [self.a, self.b]


class BackToBack(Constraint):
    def __init__(self, a_object_id: str, b_object_id: str):
        self.a = a_object_id
        self.b = b_object_id

    def weights(self) -> dict[str, float]:
        return {self.a: 1, self.b: 1}

    def objects(self) -> list[str]:
        return [self.a, self.b]


class SideBySide(Constraint):
    def __init__(self, a_object_id: str, b_object_id: str):
        self.a = a_object_id
        self.b = b_object_id

    def weights(self) -> dict[str, float]:
        return {self.a: 1, self.b: 1}

    def objects(self) -> list[str]:
        return [self.a, self.b]


class SceneObject:
    LOCKED = 0b01
    REMOVED = 0b10

    def __init__(self, id: str):
        self.id = id
        self.choices = list[Furniture]()
        self.semantic_name = ""
        self.description = ""
        self.flags = 0
        self.x: int = 0
        self.y: int = 0
        self.z: int = 0
        self.yaw: float = 0

    def add_choice(self, furniture: Furniture):
        self.choices.append(furniture)

    def add_choices(self, furniture: Iterable[Furniture]):
        self.choices.extend(furniture)

    def get_choices(self) -> list[Furniture]:
        return self.choices

    def mark_removed(self):
        self.flags = self.flags | SceneObject.REMOVED

    def unlock_location(self):
        self.flags = self.flags & ~SceneObject.LOCKED

    def lock_at_location(self, x: int, y: int, z: int, yaw: float):
        self.x = x
        self.y = y
        self.z = z
        self.yaw = yaw
        self.flags = self.flags | SceneObject.LOCKED

    def describe(self, description: str):
        self.description = description

    def set_semantic_name(self, name: str):
        self.semantic_name = name.lower()


class SceneGraph:
    def __init__(self, project: Project):
        self.project = project
        self.objects = dict[str, SceneObject]()
        self.constraints = dict[str, list[Constraint]]()

    def get_or_create_object(self, id: str) -> SceneObject:
        object = self.objects.get(id)
        if object:
            return object
        object = SceneObject(id)
        self.objects[id] = object
        return object

    def get_or_create_object_by_semantic_name(
        self, name: str
    ) -> tuple[SceneObject, bool]:
        object = self.find_object_by_semantic_name(name)
        if object:
            return object, True
        id = uuid4().hex
        object = SceneObject(id)
        self.objects[id] = object
        object.set_semantic_name(name)
        return object, False

    def find_object_by_semantic_name(self, name: str) -> SceneObject | None:
        for object in self.objects.values():
            if object.semantic_name.lower() == name.lower():
                return object
        return None

    def add_constraint(self, constraint: Constraint):
        for object_id in constraint.objects():
            current = self.constraints.get(object_id, [])
            current.append(constraint)
            self.constraints[object_id] = current

    def iter_objects(self) -> Iterable[SceneObject]:
        return self.objects.values()

    def mutate(self) -> "SceneGraph": ...

    def describe(self) -> str:
        # TODO: more spatial description (which objects are around, near or far from
        # walls, room type).

        if len(self.objects) == 0:
            return "An empty apartment"

        furniture_descriptions = list[str]()
        for object in self.objects.values():
            if not object.semantic_name:
                continue
            furniture_descriptions.append(object.semantic_name)
        return "Furniture:\n" + "\n".join(
            map(lambda d: f" - {d}", furniture_descriptions)
        )

    def to_plan(self) -> Plan: ...
