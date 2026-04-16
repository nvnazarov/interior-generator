import numpy as np
from typing import Literal, Any

Vec2 = np.ndarray[tuple[int, int], np.dtype[np.float64]]
Vec3 = np.ndarray[tuple[int, int, int], np.dtype[np.float64]]


NORTH = np.asarray([0, 1])
SOUTH = np.asarray([0, -1])
EAST = np.asarray([1, 0])
WEST = np.asarray([-1, 0])


def distance_point_to_segment_along_direction(p: Vec2, a: Vec2, b: Vec2, d: Vec2):
    x = projection_point_to_line(p, a, b)
    h = x - p
    hn = np.linalg.norm(h)
    return hn * hn * np.linalg.norm(d) / np.dot(h, d)


def projection_point_to_line(p: Vec2, a: Vec2, b: Vec2) -> Vec2:
    ab = b - a
    ap = p - a
    t = np.dot(ap, ab) / np.dot(ab, ab)
    return a + t * ab


def distance_point_to_line(p: Vec2, a: Vec2, b: Vec2):
    ab = b - a
    ap = p - a
    d = np.linalg.norm(np.cross(ab, ap)) / np.linalg.norm(ab)
    return d


def distance_par_to_par(
    a: Vec3, a_size: Vec3, a_dir: Vec3, b: Vec3, b_size: Vec3, b_dir: Vec3
):
    # Rough approximation for faster computation.
    return max(np.linalg.norm(b - a) - np.min(a_size / 2) - np.min(b_size / 2), 0)


def direction_to_nswe(d: Vec2) -> Literal["north", "south", "west", "east"]:
    v = list[tuple[Literal["north", "south", "west", "east"], Any]](
        [
            ("north", NORTH),
            ("south", SOUTH),
            ("west", WEST),
            ("east", EAST),
        ]
    )
    return sorted(v, key=lambda x: np.linalg.norm(d - x[1]))[0][0]


def location_as_text() -> Literal["to the left", "to the right", "above", "under"]:
    return "above"
