from io import BytesIO

import ezdxf.filemanagement
from ezdxf.lldxf.const import DXF2018
from ezdxf.units import CM


class DXFRenderer:
    def __init__(self, buffer: BytesIO):
        self.doc = ezdxf.filemanagement.new(DXF2018, False, units=CM)
        self.buffer = buffer

    def draw_plan(self):
        pass

    def flush(self):
        self.doc.write(self.buffer)
