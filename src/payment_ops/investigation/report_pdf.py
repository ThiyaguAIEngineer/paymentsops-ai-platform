"""ReportLab presentation only; no investigation actions or evaluation rules."""

from functools import partial
from io import BytesIO
from pathlib import Path
from threading import Lock
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import reportlab
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from payment_ops.investigation.report import CaseReport, DISCLAIMER


_FONT_LOCK = Lock()


def _fonts():
    # Bundled fonts keep exports portable; no OS font/network requirement.
    with _FONT_LOCK:
        for name, file in (("CaseSans", "Vera.ttf"), ("CaseSansBold", "VeraBd.ttf")):
            if name not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont(name, str(Path(reportlab.__file__).parent / "fonts" / file)))


def render_case_report(report: CaseReport) -> bytes:
    """Render projected facts using flowing paragraphs and splittable rows."""
    out = BytesIO()
    _fonts()
    navy, teal = colors.HexColor("#16324F"), colors.HexColor("#087F8C")
    body = ParagraphStyle("Body", fontName="CaseSans", fontSize=9, leading=13,
                          textColor=navy, splitLongWords=True, alignment=TA_LEFT)
    label = ParagraphStyle("Label", parent=body, fontName="CaseSansBold", fontSize=8)
    heading = ParagraphStyle("Heading", parent=body, fontName="CaseSansBold", fontSize=12,
                             leading=16, spaceBefore=15, spaceAfter=7, keepWithNext=True)
    title = ParagraphStyle("Title", parent=heading, fontSize=24, leading=29, spaceAfter=12)

    def p(value, style=body):
        # Treat all model/reviewer values as literal text, never ReportLab markup.
        return Paragraph(escape(value).replace("\n", "<br/>"), style)

    story = [p("PAYMENTOPS", heading), p("Investigation Case Report", title),
             p("PROVISIONAL - awaiting human review" if report.provisional
               else "Recorded investigation outcome", heading), p(DISCLAIMER), Spacer(1, 12)]
    for section in report.sections:
        story.append(p(section.title, heading))
        rows = [[p(k, label), p(v)] for k, v in section.rows]
        table = Table(rows, colWidths=[143, A4[0] - 239], hAlign="LEFT", splitInRow=1)
        table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EDF4F7")),
            ("LINEBELOW", (0, 0), (-1, -1), 0.35, colors.HexColor("#D5E2E8")),
            ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]))
        story.append(table)

    def page(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(teal)
        canvas.setLineWidth(2)
        canvas.line(48, A4[1] - 34, A4[0] - 48, A4[1] - 34)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(navy)
        canvas.drawString(48, 30, "PaymentOps | Synthetic data | No payment authorization")
        canvas.drawRightString(A4[0] - 48, 30, f"Page {doc.page}")
        canvas.restoreState()

    doc = SimpleDocTemplate(out, pagesize=A4, leftMargin=48, rightMargin=48,
                            topMargin=48, bottomMargin=48, title="PaymentOps Investigation Case Report",
                            author="PaymentOps", pageCompression=1, invariant=1)
    doc.build(story, onFirstPage=page, onLaterPages=page, canvasmaker=partial(Canvas, invariant=1))
    return out.getvalue()
