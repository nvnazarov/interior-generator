import logging
from io import BytesIO
from typing import NamedTuple, cast

import numpy as np
from reportlab.lib.colors import (
    Color,
    black,
    blue,
    brown,
    green,
    grey,
    red,
    white,
    yellow,
)
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas

from app.core.catalog import Catalog
from app.core.models import Plan, Project

logger = logging.getLogger(__name__)

Vec2 = np.ndarray[tuple[int, int], np.dtype[np.float64]]


def get_area_color(type: str) -> Color:
    match type:
        case "kitchen":
            return red
        case "bathroom":
            return blue
        case "bedroom":
            return green
        case "livingroom":
            return yellow
        case "hallway":
            return grey
        case _:
            logger.warning({"msg": "unknow area type", "type": type})
            return grey


def get_area_name(type: str) -> str:
    match type:
        case "kitchen":
            return "Kitchen"
        case "bathroom":
            return "Bathroom"
        case "bedroom":
            return "Bedroom"
        case "livingroom":
            return "Living room"
        case "hallway":
            return "Hallway"
        case _:
            logger.warning({"msg": "unknow area type", "type": type})
            return "Unknown"


def calc_polygon_area(
    points: list[Plan.Content.Area.Point] | list[Project.Content.WetArea.Point],
) -> float:
    """
    Shoelace formula with trapezoids.
    """

    area = 0
    for i in range(len(points)):
        a = points[i]
        b = points[(i + 1) % len(points)]
        area += (a.y + b.y) * (a.x - b.x) / 2
    return abs(area) / 10000


def vec2(x: float, y: float) -> Vec2:
    return np.asarray([x, y], dtype=np.float64)  # type: ignore


def left(v: Vec2) -> Vec2:
    return vec2(-v[1], v[0])


def right(v: Vec2) -> Vec2:
    return vec2(v[1], -v[0])


WALL_COLOR = black
WINDOW_COLOR = blue
DOOR_COLOR = brown

WALL_WIDTH = 20


class Legend:
    class Record(NamedTuple):
        type: str
        area: float

    def __init__(self):
        self._areas = dict[str, float]()

    def add(self, type: str, area: float):
        if area != 0:
            self._areas[type] = self._areas.get(type, 0) + area

    def records(self) -> list[Record]:
        return [Legend.Record(type, area) for type, area in self._areas.items()]


class PDFRenderer:
    def __init__(self, buffer: BytesIO):
        pagesize = landscape(A4)
        self._c = canvas.Canvas(buffer, pagesize=pagesize)
        self._width, self._height = pagesize
        self._padding = cm

    def draw_project(self, project: Project):
        # Calculate bounds.
        h = WALL_WIDTH / 2
        min_x = 1e6
        min_y = 1e6
        max_x = -1e6
        max_y = -1e6
        for area in project.content.wet_areas.values():
            for point in area.points:
                min_x = min(point.x, min_x)
                max_x = max(point.x, max_x)
                min_y = min(point.y, min_y)
                max_y = max(point.y, max_y)
        for wall in project.content.walls.values():
            if wall.x1 == wall.x2 or wall.y1 == wall.y2:
                min_x = min(wall.x1 - h, wall.x2 - h, min_x)
                max_x = max(wall.x1 + h, wall.x2 + h, max_x)
                min_y = min(wall.y1 - h, wall.y2 - h, min_y)
                max_y = max(wall.y1 + h, wall.y2 + h, max_y)
            else:
                a = vec2(wall.x1, wall.y1)
                b = vec2(wall.x2, wall.y2)
                d = cast(Vec2, a - b)
                d *= h / np.linalg.norm(d)
                p1 = a + d + left(d)
                p2 = a + d + right(d)
                p3 = b - d + left(d)
                p4 = b - d + right(d)
                min_x = min(p1[0], p2[0], p3[0], p4[0], min_x)
                max_x = max(p1[0], p2[0], p3[0], p4[0], max_x)
                min_y = min(p1[1], p2[1], p3[1], p4[1], min_y)
                max_y = max(p1[1], p2[1], p3[1], p4[1], max_y)

        # Apply padding transforms.
        self._c.saveState()
        self._c.translate(self._padding, self._padding)
        self._c.rect(
            0, 0, self._width - 2 * self._padding, self._height - 2 * self._padding
        )

        # Apply project transforms.
        self._c.saveState()
        w = max_x - min_x
        h = max_y - min_y
        real_w = w * cm
        real_h = h * cm
        available_w = self._width - 2 * self._padding
        available_h = self._height - 2 * self._padding - 1 * cm
        real_scale = int(np.ceil(max(1, real_w / available_w, real_h / available_h)))
        scale = cm / real_scale
        self._c.scale(scale, scale)
        self._c.translate(-min_x, -min_y)

        # Draw fuctional areas.
        for area in project.content.wet_areas.values():
            self._draw_area(area.points, blue)

        # Draw walls.
        self._c.saveState()
        self._c.setStrokeColor(black)
        self._c.setLineWidth(20)
        for wall in project.content.walls.values():
            if wall.x1 == wall.x2 and wall.y1 == wall.y2:
                logger.warning({"msg": "wall has 0 length"})
                continue
            a = np.asarray([wall.x1, wall.y1], dtype=np.float64)
            b = np.asarray([wall.x2, wall.y2], dtype=np.float64)
            d = b - a
            d /= np.linalg.norm(d)  # type: ignore
            b += d * 10
            a -= d * 10
            self._c.line(a[0], a[1], b[0], b[1])
        self._c.restoreState()

        # Draw doors.
        self._c.saveState()
        self._c.setStrokeColor(white)
        self._c.setLineWidth(20.2)
        for door in project.content.doors.values():
            wall = project.content.walls.get(door.wall_id)
            if wall is None:
                logger.warning({"msg": "door is not attached to wall"})
                continue
            a = np.asarray([wall.x1, wall.y1], dtype=np.float64)
            b = np.asarray([wall.x2, wall.y2], dtype=np.float64)
            d = b - a
            d /= np.linalg.norm(d)  # type: ignore
            a += d * door.x
            b = a + d * door.w
            self._c.line(a[0], a[1], b[0], b[1])
        self._c.restoreState()

        # Draw windows.
        self._c.saveState()
        self._c.setStrokeColor(blue)
        self._c.setLineWidth(16)
        for window in project.content.windows.values():
            wall = project.content.walls.get(window.wall_id)
            if wall is None:
                logger.warning({"msg": "window is not attached to wall"})
                continue
            if window.w == 0 or window.h == 0:
                logger.warning({"msg": "window has 0 size"})
                continue
            a = np.asarray([wall.x1, wall.y1], dtype=np.float64)
            b = np.asarray([wall.x2, wall.y2], dtype=np.float64)
            d = b - a
            d /= np.linalg.norm(d)  # type: ignore
            a += d * window.x
            b = a + d * window.w
            self._c.line(a[0], a[1], b[0], b[1])
        self._c.restoreState()

        # Drop plan transforms.
        self._c.restoreState()

        # Draw project's name and scale.
        self._c.setFont("main", 14)
        self._c.drawString(
            2 * mm,
            self._height - 2 * self._padding - 14 - 2 * mm,
            project.name or "Untitled",
        )
        self._c.drawCentredString(
            (self._width - 2 * self._padding) / 2,
            self._height - 2 * self._padding - 14 - 2 * mm,
            f"SCALE 1:{real_scale}",
        )

        # Drop padding transforms.
        self._c.restoreState()

        self._c.showPage()

    async def draw_plan(self, project: Project, plan: Plan, catalog: Catalog):
        # Calculate bounds and add legend records.
        h = WALL_WIDTH / 2
        min_x = 1e6
        min_y = 1e6
        max_x = -1e6
        max_y = -1e6
        for area in project.content.wet_areas.values():
            for point in area.points:
                min_x = min(point.x, min_x)
                max_x = max(point.x, max_x)
                min_y = min(point.y, min_y)
                max_y = max(point.y, max_y)
        for wall in project.content.walls.values():
            if wall.x1 == wall.x2 or wall.y1 == wall.y2:
                min_x = min(wall.x1 - h, wall.x2 - h, min_x)
                max_x = max(wall.x1 + h, wall.x2 + h, max_x)
                min_y = min(wall.y1 - h, wall.y2 - h, min_y)
                max_y = max(wall.y1 + h, wall.y2 + h, max_y)
            else:
                a = vec2(wall.x1, wall.y1)
                b = vec2(wall.x2, wall.y2)
                d = cast(Vec2, a - b)
                d *= h / np.linalg.norm(d)
                p1 = a + d + left(d)
                p2 = a + d + right(d)
                p3 = b - d + left(d)
                p4 = b - d + right(d)
                min_x = min(p1[0], p2[0], p3[0], p4[0], min_x)
                max_x = max(p1[0], p2[0], p3[0], p4[0], max_x)
                min_y = min(p1[1], p2[1], p3[1], p4[1], min_y)
                max_y = max(p1[1], p2[1], p3[1], p4[1], max_y)
        for area in plan.content.areas.values():
            for point in area.points:
                min_x = min(point.x, min_x)
                max_x = max(point.x, max_x)
                min_y = min(point.y, min_y)
                max_y = max(point.y, max_y)
        for meta in plan.content.furniture.values():
            furniture = await catalog.find_furniture_by_id(meta.furniture_id)
            if furniture is None:
                logger.warning(
                    {
                        "msg": "cannot find furniure in the catalog",
                        "id": meta.furniture_id,
                    }
                )
                continue
            cos = np.cos(meta.yaw)
            sin = np.sin(meta.yaw)
            w = furniture.width / 2
            d = furniture.depth / 2
            min_x = min(meta.x - abs(w * cos), meta.x - abs(d * sin), min_x)
            max_x = max(meta.x + abs(w * cos), meta.x + abs(d * sin), max_x)
            min_y = min(meta.z - abs(w * sin), meta.z - abs(d * cos), min_y)
            max_y = max(meta.z + abs(w * sin), meta.z + abs(d * cos), max_y)

        # Apply padding transforms.
        self._c.saveState()
        self._c.translate(self._padding, self._padding)
        self._c.rect(
            0, 0, self._width - 2 * self._padding, self._height - 2 * self._padding
        )

        # Apply plan transforms.
        self._c.saveState()
        w = max_x - min_x
        h = max_y - min_y
        real_w = w * cm
        real_h = h * cm
        available_w = self._width - 2 * self._padding
        available_h = self._height - 2 * self._padding - 1 * cm
        real_scale = int(np.ceil(max(1, real_w / available_w, real_h / available_h)))
        scale = cm / real_scale
        self._c.scale(scale, scale)
        self._c.translate(-min_x, -min_y)

        # Draw fuctional areas.
        for area in plan.content.areas.values():
            color = get_area_color(area.type)
            self._draw_area(area.points, color)

        # Draw furniture.
        ordered_metas = sorted(plan.content.furniture.values(), key=lambda m: m.y)
        for meta in ordered_metas:
            furniture = await catalog.find_furniture_by_id(meta.furniture_id)
            if furniture is None:
                logger.warning(
                    {
                        "msg": "cannot find furniure in the catalog",
                        "id": meta.furniture_id,
                    }
                )
                continue
            self._c.saveState()
            self._c.setLineWidth(1)
            self._c.setStrokeColor(black)
            self._c.setFillColor(white)
            self._c.setFont("main", 7)
            self._c.translate(meta.x, meta.z)
            self._c.rotate(meta.yaw * 180 / np.pi)
            w = furniture.width / 2
            d = furniture.depth / 2
            self._c.rect(-w, -d, furniture.width, furniture.depth, fill=1)
            self._c.setFillColor(black)
            self._c.drawString(-w + mm, -d + mm, furniture.name)
            self._c.restoreState()

        # Draw walls.
        self._c.saveState()
        self._c.setStrokeColor(black)
        self._c.setLineWidth(20)
        for wall in project.content.walls.values():
            if wall.x1 == wall.x2 and wall.y1 == wall.y2:
                logger.warning({"msg": "wall has 0 length"})
                continue
            a = np.asarray([wall.x1, wall.y1], dtype=np.float64)
            b = np.asarray([wall.x2, wall.y2], dtype=np.float64)
            d = b - a
            d /= np.linalg.norm(d)  # type: ignore
            b += d * 10
            a -= d * 10
            self._c.line(a[0], a[1], b[0], b[1])
        self._c.restoreState()

        # Draw doors.
        self._c.saveState()
        self._c.setStrokeColor(white)
        self._c.setLineWidth(20.2)
        for door in project.content.doors.values():
            wall = project.content.walls.get(door.wall_id)
            if wall is None:
                logger.warning({"msg": "door is not attached to wall"})
                continue
            a = np.asarray([wall.x1, wall.y1], dtype=np.float64)
            b = np.asarray([wall.x2, wall.y2], dtype=np.float64)
            d = b - a
            d /= np.linalg.norm(d)  # type: ignore
            a += d * door.x
            b = a + d * door.w
            self._c.line(a[0], a[1], b[0], b[1])
        self._c.restoreState()

        # Draw windows.
        self._c.saveState()
        self._c.setStrokeColor(blue)
        self._c.setLineWidth(16)
        for window in project.content.windows.values():
            wall = project.content.walls.get(window.wall_id)
            if wall is None:
                logger.warning({"msg": "window is not attached to wall"})
                continue
            if window.w == 0 or window.h == 0:
                logger.warning({"msg": "window has 0 size"})
                continue
            a = np.asarray([wall.x1, wall.y1], dtype=np.float64)
            b = np.asarray([wall.x2, wall.y2], dtype=np.float64)
            d = b - a
            d /= np.linalg.norm(d)  # type: ignore
            a += d * window.x
            b = a + d * window.w
            self._c.line(a[0], a[1], b[0], b[1])
        self._c.restoreState()

        # Drop plan transforms.
        self._c.restoreState()

        # Draw a legend.
        legend = Legend()
        for area in plan.content.areas.values():
            legend.add(area.type, calc_polygon_area(area.points))
        records = legend.records()
        if len(records) != 0:
            self._c.saveState()
            self._c.setFont("main", 12)
            n = len(records)
            h = 0.5 * cm
            self._c.setLineWidth(1)
            self._c.translate(
                self._width - 2 * self._padding - 8 * cm,
                self._height - 2 * self._padding - 1 * cm - (n + 1) * h,
            )
            self._c.setFillColor(white)
            self._c.rect(0, 0, 8 * cm, 1 * cm + (n + 1) * h, fill=1)
            for i in range(1, n + 1):
                record = records[i - 1]
                color = get_area_color(record.type)
                fill = Color(
                    red=color.red, green=color.green, blue=color.blue, alpha=0.5
                )
                self._c.setFillColor(fill)
                self._c.rect(0, h * i, 8 * cm, h, fill=1)
                self._c.setFillColor(black)
                self._c.drawCentredString(0.5 * cm, h * i + mm, str(n - i + 1))
                self._c.drawString(1.2 * cm, h * i + mm, get_area_name(record.type))
                self._c.drawCentredString(6.5 * cm, h * i + mm, f"{record.area:.2f}")
            self._c.setStrokeColor(black)
            self._c.grid(  # type: ignore
                [0, 1 * cm, 5 * cm, 8 * cm],
                [i * h for i in range(n + 2)] + [(n + 1) * h + 1 * cm],
            )
            self._c.drawCentredString(0.5 * cm, h * (n + 1) + 3 * mm, "№")
            self._c.drawCentredString(3 * cm, h * (n + 1) + 3 * mm, "Name")
            self._c.drawCentredString(6.5 * cm, h * (n + 1) + 3 * mm, "Area, sq.m.")
            self._c.drawCentredString(
                6.5 * cm,
                mm,
                f"{sum([r.area for r in records]):.2f}",
            )
            self._c.restoreState()

        # Draw plan's name and scale.
        self._c.setFont("main", 14)
        self._c.drawString(
            2 * mm,
            self._height - 2 * self._padding - 14 - 2 * mm,
            plan.name or "Untitled",
        )
        self._c.drawCentredString(
            (self._width - 2 * self._padding) / 2,
            self._height - 2 * self._padding - 14 - 2 * mm,
            f"SCALE 1:{real_scale}",
        )

        # Drop padding transforms.
        self._c.restoreState()

        self._c.showPage()

    def _draw_area(
        self,
        points: list[Plan.Content.Area.Point] | list[Project.Content.WetArea.Point],
        color: Color,
    ):
        if len(points) < 3:
            logger.warning({"msg": "area has less than 3 points"})
            return
        self._c.saveState()
        fill = Color(red=color.red, green=color.green, blue=color.blue, alpha=0.5)
        self._c.setFillColor(fill)
        self._c.setStrokeColor(color)
        self._c.setLineWidth(2)
        path = self._c.beginPath()
        path.moveTo(points[0].x, points[0].y)  # type: ignore
        for point in points[1:]:
            path.lineTo(point.x, point.y)  # type: ignore
        path.close()
        self._c.drawPath(path, fill=1)  # type: ignore
        self._c.restoreState()

    def close(self):
        self._c.save()
