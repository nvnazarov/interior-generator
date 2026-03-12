from io import BytesIO
from typing import AsyncIterable, Iterable, NamedTuple

from reportlab.lib.colors import Color, black, brown, green, red, yellow
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas

from app.core.models import Area, AreaType, Plan, Project, Wall, Window

AREA_COLORS = {
    AreaType.KITCHEN: red,
    AreaType.BATHROOM: yellow,
    AreaType.BEDROOM: green,
    AreaType.LIVINGROOM: brown,
}


class LegendRecord(NamedTuple):
    name: str
    area_sqm: float
    color: Color


class PDFRenderer:
    def __init__(self, buffer: BytesIO):
        pagesize = landscape(A4)
        self.c = canvas.Canvas(buffer, pagesize=pagesize)
        self.width, self.height = pagesize
        self.padding = cm
        # self.plan_box = Vec4(cm, cm, self.width - 11 * cm, self.height - 2 * cm)

    def draw_project(self, project: Project):
        self.c.saveState()
        self.c.rect(
            self.padding,
            self.padding,
            self.width - 2 * self.padding,
            self.height - 2 * self.padding,
        )
        self.c.setFont("main", 14)
        self.c.drawString(
            self.padding + 2,
            self.height - self.padding - 16,
            project.name or "Untitled Project",
        )
        self.c.restoreState()
        self.c.showPage()

    def draw_plan(self, plan: Plan):
        # Calculate the plans scale to fit the page.
        # boundary = plan.boundary()
        # scale = max(
        #     1,
        #     math.ceil(boundary.w * cm / self.plan_box.w),
        #     math.ceil(boundary.h * cm / self.plan_box.h),
        # )

        # Draw aside information.
        self.c.saveState()
        self.c.setDash((1 * mm, 2 * mm))
        self.c.setStrokeColor(black)
        self.c.setStrokeAlpha(0.2)
        self.c.rect(
            self.padding,
            self.padding,
            self.width - 11 * cm,
            self.height - 2 * self.padding,
        )
        self.c.restoreState()
        self.draw_name(plan.name)
        # self.draw_scale(scale)
        legend_records: list[LegendRecord] = []
        # for area in plan.areas:
        #     if area.type != AreaType.WET_AREA:
        #         legend_records.append(
        #             LegendRecord(
        #                 area.type, area.area_sqm(), AREA_COLORS.get(area.type, white)
        #             )
        #         )
        self.draw_legend(legend_records)

        # Draw the plan itself.
        # plan.translate(-boundary.x, -boundary.y)
        # plan.scale(cm / scale)
        self.c.saveState()
        # self.c.translate(self.padding, self.padding)
        # for area in plan.areas:
        #     self.draw_area(area, AREA_COLORS.get(area.type, white))
        # self.draw_walls(plan.walls.values(), scale)
        self.c.restoreState()

        self.next()

    def draw_name(self, name: str):
        self.c.saveState()
        self.c.setFont("main", 14)
        self.c.drawString(self.padding, self.height - self.padding - 14, name)
        self.c.restoreState()

    def draw_scale(self, ratio: int):
        self.c.saveState()
        self.c.setFont("main", 14)
        self.c.drawRightString(
            self.width - 9 * cm - self.padding,
            self.height - self.padding - 14,
            f"МАСШТАБ 1:{ratio}",
        )
        self.c.restoreState()

    def draw_walls(self, walls: Iterable[Wall], scale: int):
        self.c.saveState()
        self.c.setLineWidth(cm / scale)
        self.c.setStrokeColor(black)
        self.c.lines([(w.x1, w.y1, w.x2, w.y2) for w in walls])  # type: ignore
        self.c.restoreState()

    def draw_furniture(self):
        # x, y, _, _ = self._scale(furniture.x, furniture.y, 0, 0)
        # self.c.setStrokeColor(blue)
        # self.c.rect(x, y, w, h, stroke=1, fill=0)
        # self.c.drawString(x + 3, y + h - 12, area.type)
        pass

    def draw_windows(self, wall: Wall, window: Window):
        pass

    def draw_doors(self):
        pass

    def draw_area(self, area: Area, color: Color):
        self.c.saveState()
        self.c.setStrokeColor(color)
        fill = Color(red=color.red, green=color.green, blue=color.blue, alpha=0.5)
        self.c.setFillColor(fill)
        self.c.rect(area.x, area.y, area.w, area.h, stroke=1, fill=1)
        self.c.restoreState()

    def draw_legend(self, records: list[LegendRecord]):
        self.c.saveState()
        self.c.setFont("main", 14)
        if len(records) == 0:
            return
        n = len(records)
        pad = 1 * cm
        h = 0.5 * cm
        self.c.setLineWidth(1)
        self.c.translate(
            self.width - pad - 8 * cm, self.height - pad - 1 * cm - (n + 1) * h
        )
        for i in range(1, n + 1):
            color = records[i - 1].color
            fill = Color(red=color.red, green=color.green, blue=color.blue, alpha=0.5)
            self.c.setFillColor(fill)
            self.c.rect(0, h * i, 8 * cm, h, fill=1)
            self.c.setFillColor(black)
            self.c.drawCentredString(0.5 * cm, h * i + mm, str(n - i + 1))
            self.c.drawString(1.2 * cm, h * i + mm, records[i - 1].name)
            self.c.drawCentredString(6.5 * cm, h * i + mm, str(records[i - 1].area_sqm))
        self.c.setStrokeColor(black)
        self.c.grid(
            [0, 1 * cm, 5 * cm, 8 * cm],
            [i * h for i in range(n + 2)] + [(n + 1) * h + 1 * cm],
        )  # type: ignore
        self.c.drawCentredString(0.5 * cm, h * (n + 1) + 3 * mm, "№")
        self.c.drawCentredString(3 * cm, h * (n + 1) + 3 * mm, "Наименование")
        self.c.drawCentredString(6.5 * cm, h * (n + 1) + 3 * mm, "Площадь")
        self.c.drawCentredString(
            6.5 * cm,
            mm,
            str(sum([r.area_sqm for r in records])),
        )
        self.c.restoreState()

    def next(self):
        self.c.showPage()

    def close(self):
        self.c.save()


async def export_pdf(project: Project, plans: AsyncIterable[Plan]) -> BytesIO:
    buffer = BytesIO()
    renderer = PDFRenderer(buffer)
    renderer.draw_project(project)
    async for plan in plans:
        renderer.draw_plan(plan)
    renderer.close()
    buffer.seek(0)
    return buffer
