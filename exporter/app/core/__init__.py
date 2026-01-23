from pathlib import Path

from reportlab.pdfbase import pdfmetrics, ttfonts

pdfmetrics.registerFont(  # type: ignore
    ttfonts.TTFont(
        "main", Path(__file__).parent.parent / "assets" / "IBMPlexMono-Regular.ttf"
    )
)
