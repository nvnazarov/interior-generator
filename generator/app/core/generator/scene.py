import logging
from typing import Iterable
from abc import ABC, abstractmethod
from uuid import uuid4
import random
from pydantic import BaseModel
from app.core.generator.geometry import (
    vec2,
    vec3,
    direction,
    yaw,
    scale,
    left,
    right,
    norm,
    distance_point_to_segment,
    intersect_par_seg,
    random_yaw,
    opposite_yaw,
)
from itertools import pairwise

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

    @abstractmethod
    def locations(self, scene: "SceneGraph", object_id: str) -> "LocationsCollection":
        """
        Computes possible locations for the object in
        the scene according to this constraint.
        """
        pass


class OnFloor(Constraint):
    def __init__(self, object_id: str):
        self.object_id = object_id

    def weights(self) -> dict[str, float]:
        return {self.object_id: 0}

    def objects(self) -> list[str]:
        return [self.object_id]

    def locations(self, scene: "SceneGraph", object_id: str) -> "LocationsCollection":
        if self.object_id == object_id:
            object = scene.objects.get(object_id)
            if not object:
                raise ValueError("Object does not exist on scene")
            bounds = scene.bounds()
            return SampleLocationsCollection(
                [
                    Location(x=x, y=object.height // 2, z=z, yaw=0)
                    for x in range(bounds[0], bounds[0] + bounds[2], 10)
                    for z in range(bounds[1], bounds[1] + bounds[3], 10)
                ],
                any_yaw=True,
            )
        return AnyLocation()

    def __str__(self):
        return f"[on floor({self.object_id})]"


class FarWall(Constraint):
    def __init__(self, object_id: str):
        self.object_id = object_id

    def weights(self) -> dict[str, float]:
        return {self.object_id: 0.1}

    def objects(self) -> list[str]:
        return [self.object_id]

    def locations(self, scene: "SceneGraph", object_id: str) -> "LocationsCollection":
        if self.object_id == object_id:
            object = scene.objects.get(object_id)
            if not object:
                raise ValueError("Object does not exist on scene")
            bounds = scene.bounds()
            locations = list[Location]()
            for x in range(bounds[0], bounds[0] + bounds[2], 20):
                for z in range(bounds[1], bounds[1] + bounds[3], 20):
                    p = vec2(x, z)
                    close_to_wall = False
                    for wall in scene.project.content.walls.values():
                        a = vec2(wall.x1, wall.y1)
                        b = vec2(wall.x2, wall.y2)
                        if distance_point_to_segment(p, a, b) < 100:
                            close_to_wall = True
                            break
                    if close_to_wall:
                        continue
                    # TODO: verify that point is inside the apartment (not only
                    # inside the bbox).
                    locations.append(Location(x=x, y=object.height // 2, z=z, yaw=0))
            return SampleLocationsCollection(locations, any_yaw=True)
        return AnyLocation()

    def __str__(self):
        return f"[far wall({self.object_id})]"


class AgainstWall(Constraint):
    def __init__(self, object_id: str):
        self.object_id = object_id

    def weights(self) -> dict[str, float]:
        return {self.object_id: 0}

    def objects(self) -> list[str]:
        return [self.object_id]

    def locations(self, scene: "SceneGraph", object_id: str) -> "LocationsCollection":
        if self.object_id == object_id:
            object = scene.objects.get(object_id)
            if not object:
                raise ValueError("Object does not exist on scene")
            locations = list[Location]()
            h = object.depth // 2 + 10
            for wall in scene.project.content.walls.values():
                v = vec2(wall.x1, wall.x2)
                w = vec2(wall.x2 - wall.x1, wall.y2 - wall.y1)
                step = scale(w, 50)
                l_yaw = yaw(left(step))
                r_yaw = yaw(right(step))
                for _ in range(round(norm(w) / norm(step))):
                    anchor = Location(x=int(v[0]), y=object.height // 2, z=int(v[1]))
                    locations.append(anchor.left(h).modify(yaw=l_yaw))
                    locations.append(anchor.right(h).modify(yaw=r_yaw))
                    v += step
            return SampleLocationsCollection(locations)
        return AnyLocation()

    def __str__(self):
        return f"[against wall({self.object_id})]"


class InFrontOf(Constraint):
    def __init__(self, a_object_id: str, b_object_id: str):
        self.a = a_object_id
        self.b = b_object_id

    def weights(self) -> dict[str, float]:
        return {self.a: 0, self.b: 0}

    def objects(self) -> list[str]:
        return [self.a, self.b]

    def locations(self, scene: "SceneGraph", object_id: str) -> "LocationsCollection":
        if self.a == object_id or self.b == object_id:
            object = scene.objects.get(object_id)
            if not object:
                raise ValueError("Object does not exist on scene")
            return SampleLocationsCollection(
                [Location(x=0, y=object.height // 2, z=0, yaw=0)]
            )
        return AnyLocation()

    def __str__(self):
        return f"[in front of(a={self.a},b={self.b})]"


class OnTopOf(Constraint):
    def __init__(self, bottom_object_id: str, top_object_id: str):
        self.bottom = bottom_object_id
        self.top = top_object_id

    def weights(self) -> dict[str, float]:
        return {self.bottom: 0, self.top: 10}

    def objects(self) -> list[str]:
        return [self.bottom, self.top]

    def locations(self, scene: "SceneGraph", object_id: str) -> "LocationsCollection":
        if self.top == object_id:
            bottom_object = scene.objects.get(self.bottom)
            top_object = scene.objects.get(object_id)
            if not top_object or not bottom_object:
                raise ValueError("Object does not exist on scene")
            if not bottom_object.placed():
                return AnyLocation()
            any_yaw = (
                bottom_object.width > top_object.width * 1.5
                and bottom_object.depth > top_object.depth * 1.5
            )
            return SampleLocationsCollection(
                [
                    Location(
                        x=bottom_object.location.x,
                        y=top_object.height // 2
                        + bottom_object.location.y
                        + bottom_object.height // 2,
                        z=bottom_object.location.z,
                        yaw=bottom_object.location.yaw,
                    )
                ],
                any_yaw=any_yaw,
            )
        return AnyLocation()

    def __str__(self):
        return f"[on top of(b={self.bottom},t={self.top})]"


class FaceToFace(Constraint):
    def __init__(self, a_object_id: str, b_object_id: str):
        self.a = a_object_id
        self.b = b_object_id

    def weights(self) -> dict[str, float]:
        return {self.a: 0, self.b: 0}

    def objects(self) -> list[str]:
        return [self.a, self.b]

    def locations(self, scene: "SceneGraph", object_id: str) -> "LocationsCollection":
        if self.a == object_id or self.b == object_id:
            object = scene.objects.get(object_id)
            anchor = scene.objects.get(self.b if self.a == object_id else self.a)
            if not object or not anchor:
                raise ValueError("Object does not exist on scene")
            if not anchor.placed():
                return AnyLocation()
            d = direction(anchor.location.yaw)
            step = d * object.depth
            p = vec2(anchor.location.x, anchor.location.z)
            p += d * (anchor.depth + object.depth) / 2
            locations = list[Location]()
            yaw = opposite_yaw(anchor.location.yaw)
            for _ in range(10):
                locations.append(
                    Location(x=int(p[0]), y=object.height // 2, z=int(p[1]), yaw=yaw)
                )
                p += step
            return SampleLocationsCollection(locations)
        return AnyLocation()

    def __str__(self):
        return f"[face to face(a={self.a},b={self.b})]"


class BackToBack(Constraint):
    def __init__(self, a_object_id: str, b_object_id: str):
        self.a = a_object_id
        self.b = b_object_id

    def weights(self) -> dict[str, float]:
        return {self.a: 0, self.b: 0}

    def objects(self) -> list[str]:
        return [self.a, self.b]

    def locations(self, scene: "SceneGraph", object_id: str) -> "LocationsCollection":
        if self.a == object_id or self.b == object_id:
            object = scene.objects.get(object_id)
            anchor = scene.objects.get(self.b if self.a == object_id else self.a)
            if not object or not anchor:
                raise ValueError("Object does not exist on scene")
            if not anchor.placed():
                return AnyLocation()
            d = -direction(anchor.location.yaw)
            step = d * object.depth
            p = vec2(anchor.location.x, anchor.location.z)
            p += d * (anchor.depth + object.depth) / 2
            locations = list[Location]()
            yaw = opposite_yaw(anchor.location.yaw)
            for _ in range(10):
                locations.append(
                    Location(x=int(p[0]), y=object.height // 2, z=int(p[1]), yaw=yaw)
                )
                p += step
            return SampleLocationsCollection(locations)
        return AnyLocation()

    def __str__(self):
        return f"[back to back(a={self.a},b={self.b})]"


class SideBySide(Constraint):
    def __init__(self, a_object_id: str, b_object_id: str):
        self.a = a_object_id
        self.b = b_object_id

    def weights(self) -> dict[str, float]:
        return {self.a: 0, self.b: 0}

    def objects(self) -> list[str]:
        return [self.a, self.b]

    def locations(self, scene: "SceneGraph", object_id: str) -> "LocationsCollection":
        if self.a == object_id or self.b == object_id:
            anchor = scene.objects.get(self.b if self.a == object_id else self.a)
            object = scene.objects.get(object_id)
            if not object or not anchor:
                raise ValueError("Object does not exist on scene")
            if not anchor.placed():
                return AnyLocation()
            anchor_location = anchor.location.model_copy()
            anchor_location.y = object.height // 2
            d = (anchor.width + object.width) / 2
            return SampleLocationsCollection(
                [anchor_location.left(d), anchor_location.right(d)]
            )
        return AnyLocation()

    def __str__(self):
        return f"[side by side(a={self.a},b={self.b})]"


class Aligned(Constraint):
    def __init__(self, target: str, anchor: str):
        self.target = target
        self.anchor = anchor

    def weights(self) -> dict[str, float]:
        return {self.target: 3, self.anchor: 0}

    def objects(self) -> list[str]:
        return [self.target, self.anchor]

    def locations(self, scene: "SceneGraph", object_id: str) -> "LocationsCollection":
        if self.target == object_id:
            anchor = scene.objects.get(self.anchor)
            object = scene.objects.get(object_id)
            if not object or not anchor:
                raise ValueError("Object does not exist on scene")
            if not anchor.placed():
                return AnyLocation()
            ws = [(anchor.width + object.width) / 2 + i * 10 for i in range(5)]
            ds = [(anchor.depth + object.depth) / 2 + i * 10 for i in range(5)]
            anchor_location = anchor.location.model_copy()
            anchor_location.y = object.height // 2
            return SampleLocationsCollection(
                [anchor_location.left(w) for w in ws]
                + [anchor_location.right(w) for w in ws]
                + [anchor_location.forward(d) for d in ds]
                + [anchor_location.backward(d) for d in ds]
            )
        return AnyLocation()

    def __str__(self):
        return f"[aligned(t={self.target},a={self.anchor})]"


class SceneObject:
    _LOCKED = 0b1
    _REMOVED = 0b10
    _PLACED = 0b100

    def __init__(self, id: str):
        self.id = id
        self.choice: Furniture | None = None
        self.choices = list[Furniture]()
        self._semantic_name = ""
        self._flags: int = 0
        self._location = Location(x=0, y=0, z=0, yaw=0)

    def choose(self, furniture: Furniture):
        if furniture not in self.choices:
            raise ValueError("furniture is not among the choices")
        self.choice = furniture

    def add_choice(self, furniture: Furniture):
        self.choices.append(furniture)
        if self.choice is None:
            self.choice = furniture

    def add_choices(self, furniture: Iterable[Furniture]):
        self.choices.extend(furniture)
        if self.choice is None and len(self.choices) > 0:
            self.choice = self.choices[0]

    def get_choices(self) -> list[Furniture]:
        return self.choices

    def remove(self):
        self._flags = self._flags | self._REMOVED

    def removed(self) -> bool:
        return bool(self._flags & self._REMOVED)

    def unlock(self):
        self._flags = self._flags & ~self._LOCKED

    def lock(self):
        self._flags = self._flags | self._LOCKED

    def locked(self) -> bool:
        return bool(self._flags & self._LOCKED)

    def placed(self) -> bool:
        return bool(self._flags & self._PLACED)

    def detach(self):
        self._flags = self._flags & ~self._PLACED

    @property
    def semantic_name(self) -> str:
        return self._semantic_name

    @semantic_name.setter
    def semantic_name(self, value: str):
        self._semantic_name = value.lower()

    @property
    def location(self) -> "Location":
        return self._location

    @location.setter
    def location(self, value: "Location"):
        if self.locked():
            raise RuntimeError("Object is locked")
        self._location = value
        self._flags = self._flags | self._PLACED

    @property
    def width(self) -> int:
        return self.choice.width if self.choice else 0

    @property
    def height(self) -> int:
        return self.choice.height if self.choice else 0

    @property
    def depth(self) -> int:
        return self.choice.depth if self.choice else 0

    def __str__(self):
        if self.semantic_name != "":
            return f"[{self.semantic_name}(id={self.id})]"
        return f"[Object(id={self.id})]"


class SceneGraph:
    def __init__(self, project: Project):
        self.project = project
        self.objects = dict[str, SceneObject]()
        self.constraints_by_object = dict[str, list[Constraint]]()
        self.constraints = list[Constraint]()
        self._bounds: tuple[int, int, int, int] | None = None

    def bounds(self) -> tuple[int, int, int, int]:
        if self._bounds:
            return self._bounds
        if len(self.project.content.walls) == 0:
            return -1000, -1000, 2000, 2000
        wall0 = next(iter(self.project.content.walls.values()))
        min_x = wall0.x1
        max_x = wall0.x1
        min_y = wall0.y1
        max_y = wall0.y1
        for wall in self.project.content.walls.values():
            min_x = min(min_x, wall.x1, wall.x2)
            max_x = max(max_x, wall.x1, wall.x2)
            min_y = min(min_y, wall.y1, wall.y2)
            max_y = max(max_y, wall.y1, wall.y2)
        self._bounds = (min_x, min_y, max_x - min_x, max_y - min_y)
        return self._bounds

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
        object.semantic_name = name
        return object, False

    def find_object_by_semantic_name(self, name: str) -> SceneObject | None:
        for object in self.objects.values():
            if object.semantic_name.lower() == name.lower():
                return object
        return None

    def add_constraint(self, constraint: Constraint):
        if constraint in self.constraints:
            return
        for object_id in constraint.objects():
            current = self.constraints_by_object.get(object_id, [])
            current.append(constraint)
            self.constraints_by_object[object_id] = current
            self.constraints.append(constraint)

    def iter_objects(self) -> Iterable[SceneObject]:
        return self.objects.values()

    def rearrange(self):
        """
        Rearrange all furniture from scratch (locked furniture is not
        moved).
        """

        for object in self.objects.values():
            if not object.locked():
                object.detach()

        objects_weights = dict[str, float]()
        for constraint in self.constraints:
            for object_id, weight in constraint.weights().items():
                current = objects_weights.get(object_id, 0.0)
                objects_weights[object_id] = current + weight

        order = sorted(
            list(self.objects.keys()),
            key=lambda object_id: objects_weights.get(object_id, 10),
        )
        logger.debug(
            {
                "msg": "placement order",
                "order": [str(self.objects[object_id]) for object_id in order],
            }
        )
        for object_id in order:
            object = self.objects[object_id]
            if not object.locked():
                logger.debug({"msg": "placing object", "object": str(object)})
                locations = AnyLocation()
                for constraint in self.constraints_by_object.get(object.id, []):
                    good_locations = constraint.locations(self, object.id)
                    locations = locations.intersect(good_locations, 5)
                    logger.debug(
                        {
                            "msg": "possible locations after applying constraint",
                            "object": str(object),
                            "locations": str(locations),
                            "constraint": str(constraint),
                        }
                    )
                some_location = locations.pick()
                if some_location:
                    object.location = some_location
                    logger.debug(
                        {
                            "msg": "placed object",
                            "object": str(object),
                            "location": str(some_location),
                        }
                    )
                else:
                    # TODO: just put the object somewhere.
                    object.location = Location()
                    logger.warning(
                        {
                            "msg": "suitable position for object were not found",
                            "object": str(object),
                        }
                    )
            else:
                logger.debug({"msg": "skipping object (locked)", "object": str(object)})

    def loss(self) -> float:
        total = 0

        # Collisions (furniture with furniture, furniture with walls,
        # furniture with doorways, furniture with windows).
        for object in self.objects.values():
            if object.removed():
                continue
            for other in self.objects.values():
                if other.removed() or other.id == object.id:
                    continue
                object_center = vec2(object.location.x, object.location.z)
                object_forward = direction(object.location.yaw) * object.depth / 2
                object_left = left(direction(object.location.yaw)) * object.width / 2
                # object_up = vec2()
                other_center = vec2(other.location.x, other.location.z)
                other_forward = direction(other.location.yaw) * other.depth / 2
                other_left = left(direction(other.location.yaw)) * other.width / 2
                object_vertices = [
                    object_center + a + b
                    for a in [object_forward, -object_forward]
                    for b in [object_left, -object_left]
                    for c in []
                ]
                other_vertices = [
                    other_center + a + b
                    for a in [other_forward, -other_forward]
                    for b in [other_left, -other_left]
                ]
            object_pivot = vec3(object.location.x, object.location.y, object.location.z)
            object_size = vec3(object.width, object.height, object.depth)
            object_dir = direction(object.location.yaw)
            for wall in self.project.content.walls.values():
                a = vec2(wall.x1, wall.y1)
                b = vec2(wall.x2, wall.y2)
                if intersect_par_seg(object_pivot, object_size, object_dir, a, b):
                    total += 1
            for door in self.project.content.doors.values():
                wall = self.project.content.walls.get(door.wall_id)
                if wall:
                    a = vec2(wall.x1, wall.y1)
                    b = vec2(wall.x2, wall.y2)
                    d = b - a
                    h = scale(left(d), door.w)  # type: ignore
                    t = scale(d, door.w / 2)  # type: ignore
                    c = a + scale(d, door.x + door.w / 2)  # type: ignore
                    for u, v in pairwise([c + m + n for m in [h, -h] for n in [t, -t]]):
                        if intersect_par_seg(
                            object_pivot, object_size, object_dir, u, v  # type: ignore
                        ):
                            total += 1
                            break
                else:
                    logger.warning({"msg": "door is attached to the non-existing wall"})
            for window in self.project.content.windows.values():
                pass

        # TODO: add other rules.

        return total

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

    def as_patch_to(self, base_plan: Plan | None) -> Plan.Patch:
        patch = Plan.Patch()
        for object in self.objects.values():
            if object.removed():
                patch.content.furniture[object.id] = None
                continue
            if not object.choice:
                logger.warning({"msg": "no choice for object", "object_id": object.id})
                continue
            if base_plan:
                old_object = base_plan.content.furniture.get(object.id)
                if (
                    old_object is not None
                    and old_object.model_dump() == object.choice.model_dump()
                ):
                    logger.debug({"msg": "object unchanged", "object_id": object.id})
                    continue
            logger.debug({"msg": "object changed", "object_id": object.id})
            patch.content.furniture[object.id] = Plan.Patch.Content.Furniture(
                furniture_id=object.choice.id,
                x=object.location.x,
                y=object.location.y,
                z=object.location.z,
                yaw=object.location.yaw,
            )
        # Mark "furniture" field as "set".
        patch.content = patch.content
        patch.content.furniture = patch.content.furniture
        return patch


class Location(BaseModel):
    x: int = 0
    y: int = 0
    z: int = 0
    yaw: float = 0

    def left(self, d: float) -> "Location":
        v = vec2(self.x, self.z)
        u = v + left(direction(self.yaw)) * d
        return Location(x=int(u[0]), y=self.y, z=int(u[1]), yaw=self.yaw)

    def right(self, d: float) -> "Location":
        v = vec2(self.x, self.z)
        u = v + right(direction(self.yaw)) * d
        return Location(x=int(u[0]), y=self.y, z=int(u[1]), yaw=self.yaw)

    def forward(self, d: float) -> "Location":
        v = vec2(self.x, self.z)
        u = v + direction(self.yaw) * d
        return Location(x=int(u[0]), y=self.y, z=int(u[1]), yaw=self.yaw)

    def backward(self, d: float) -> "Location":
        v = vec2(self.x, self.z)
        u = v - direction(self.yaw) * d
        return Location(x=int(u[0]), y=self.y, z=int(u[1]), yaw=self.yaw)

    def close_to(self, p: "Location", eps: float) -> bool:
        return (p.x - self.x) ** 2 + (p.y - self.y) ** 2 + (p.z - self.z) ** 2 < eps**2

    def modify(
        self,
        *,
        x: int | None = None,
        y: int | None = None,
        z: int | None = None,
        yaw: float | None = None,
    ) -> "Location":
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        if z is not None:
            self.z = z
        if yaw is not None:
            self.yaw = yaw
        return self

    def __str__(self):
        return f"Location[x={self.x},y={self.y},z={self.z},yaw={round(self.yaw, 2)}]"


class LocationsCollection(ABC):
    @abstractmethod
    def pick(self) -> Location | None: ...

    @abstractmethod
    def intersect(
        self, locations: "LocationsCollection", eps: float
    ) -> "LocationsCollection": ...

    @abstractmethod
    def empty(self) -> bool: ...


class AnyLocation(LocationsCollection):
    def pick(self) -> Location | None:
        return Location(x=0, y=0, z=0, yaw=0)

    def intersect(
        self, locations: "LocationsCollection", eps: float
    ) -> LocationsCollection:
        return locations

    def empty(self):
        return False

    def __str__(self):
        return "[any location]"


class NoLocation(LocationsCollection):
    def pick(self) -> Location | None:
        return None

    def intersect(
        self, locations: "LocationsCollection", eps: float
    ) -> LocationsCollection:
        return self

    def empty(self):
        return True

    def __str__(self):
        return "[no location]"


class SampleLocationsCollection(LocationsCollection):
    def __init__(self, locations: list[Location], any_yaw: bool = False):
        self.locations = locations
        self.any_yaw = any_yaw

    def pick(self) -> Location | None:
        if self.empty():
            return None
        location = random.choice(self.locations)
        if self.any_yaw:
            return location.modify(yaw=random_yaw())
        return location

    def intersect(
        self, locations: LocationsCollection, eps: float
    ) -> LocationsCollection:
        if isinstance(locations, SampleLocationsCollection):
            result = list[Location]()
            for a in self.locations:
                for b in locations.locations:
                    if a.close_to(b, eps):
                        if locations.any_yaw and not self.any_yaw:
                            result.append(a)
                        elif self.any_yaw and not locations.any_yaw:
                            result.append(b)
                        else:
                            result.append(a)
                            result.append(b)

            return SampleLocationsCollection(
                result, any_yaw=self.any_yaw and locations.any_yaw
            )
        if isinstance(locations, NoLocation):
            return locations
        if isinstance(locations, AnyLocation):
            return self
        return self

    def empty(self):
        return len(self.locations) == 0

    def __str__(self):
        return f"[sample(size={len(self.locations)})]"


class LocationsGroup(LocationsCollection):
    def __init__(self, collections: list[LocationsCollection] = []):
        self.collections = collections

    def add(self, collection: LocationsCollection):
        if not collection.empty():
            self.collections.append(collection)

    def pick(self) -> Location | None:
        if self.empty():
            return None
        return random.choice(self.collections).pick()

    def intersect(
        self, locations: LocationsCollection, eps: float
    ) -> LocationsCollection:
        # TODO
        return self

    def empty(self):
        return all([c.empty() for c in self.collections])

    def __str__(self):
        return "[group(...)]"
