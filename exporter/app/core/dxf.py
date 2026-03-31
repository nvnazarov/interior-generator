from io import StringIO
from typing import TextIO

import ezdxf.filemanagement
from ezdxf.lldxf.const import DXF2018
from ezdxf.units import CM

from app.core.models import Plan, Project


class DXFRenderer:
    def __init__(self, buffer: TextIO):
        self.doc = ezdxf.filemanagement.new(DXF2018, False, units=CM)
        self.buffer = buffer

    def draw(self, project: Project, plan: Plan):
        # TODO(nvnazarov@edu.hse.ru): drawing logic
        pass

    def flush(self):
        self.doc.write(self.buffer)


def export_dxf(project: Project, plan: Plan) -> TextIO:
    buffer = StringIO()
    renderer = DXFRenderer(buffer)
    renderer.draw(project, plan)
    renderer.flush()
    buffer.seek(0)
    return buffer
