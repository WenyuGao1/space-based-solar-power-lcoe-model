"""Build a PDF report from the generated Markdown using ReportLab."""

from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import CondPageBreak, Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _clean_inline(text: str) -> str:
    text = text.translate(str.maketrans({
        "‐": "-", "‑": "-", "‒": "-", "–": "-", "—": "-", "−": "-",
    }))
    text = text.replace("&", "&amp;")
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        r'<a href="\2" color="#0b5cad"><u>\1</u></a>',
        text,
    )
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    return text


class _ReportDocTemplate(SimpleDocTemplate):
    """Simple document template with PDF outline bookmarks for headings."""

    def afterFlowable(self, flowable: object) -> None:
        if not isinstance(flowable, Paragraph):
            return
        levels = {"Title": 0, "Heading1": 0, "Heading2": 1, "Heading3": 2}
        style_name = flowable.style.name
        if style_name not in levels:
            return
        text = flowable.getPlainText()
        bookmark_count = getattr(self, "_bookmark_count", 0) + 1
        self._bookmark_count = bookmark_count
        key = f"heading-{bookmark_count}"
        self.canv.bookmarkPage(key)
        self.canv.addOutlineEntry(text, key, level=levels[style_name], closed=False)


def _register_cjk_font() -> str:
    ttf_candidates = [
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
    ]
    for candidate in ttf_candidates:
        path = Path(candidate)
        if path.exists():
            font_name = "ArialUnicode"
            try:
                pdfmetrics.getFont(font_name)
            except KeyError:
                pdfmetrics.registerFont(TTFont(font_name, str(path)))
            return font_name

    font_name = "STSong-Light"
    try:
        pdfmetrics.getFont(font_name)
    except KeyError:
        pdfmetrics.registerFont(UnicodeCIDFont(font_name))
    return font_name


def _table_from_lines(
    lines: list[str],
    body_style: ParagraphStyle,
    max_width: float,
    header_font: str,
) -> Table | None:
    parsed: list[list[str]] = []
    for line in lines:
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if all(part == "---" for part in parts):
            continue
        parsed.append(parts)
    if not parsed:
        return None
    n_cols = max(len(row) for row in parsed)
    normalized = [row + [""] * (n_cols - len(row)) for row in parsed]
    headers = normalized[0]
    header_text = " ".join(headers).lower()
    if n_cols == 2:
        weights = [0.68, 0.32]
    elif n_cols == 3 and any(token in header_text for token in ("decision meaning", "决策含义")):
        weights = [0.22, 0.30, 0.48]
    elif n_cols == 3 and any(token in header_text for token in ("source id", "来源id")):
        weights = [0.18, 0.34, 0.48]
    elif n_cols == 3:
        weights = [0.28, 0.24, 0.48]
    elif n_cols == 4 and any(token in header_text for token in ("source", "来源")):
        weights = [0.25, 0.17, 0.26, 0.32]
    elif n_cols == 4:
        weights = [0.28, 0.18, 0.22, 0.32]
    elif n_cols == 5 and any(token in header_text for token in ("classification", "分类")):
        weights = [0.20, 0.16, 0.14, 0.16, 0.34]
    elif n_cols == 5:
        weights = [0.28, 0.16, 0.18, 0.18, 0.20]
    elif n_cols == 6:
        weights = [0.16, 0.18, 0.17, 0.17, 0.16, 0.16]
    else:
        weights = [1.0 / n_cols] * n_cols
    col_widths = [max_width * weight for weight in weights]
    table_font_size = 7.9 if n_cols == 4 else (8.0 if n_cols >= 5 else 8.3)
    table_leading = 9.4 if n_cols == 4 else (9.8 if n_cols >= 5 else 10.2)
    table_body_style = ParagraphStyle(
        "TableCell",
        parent=body_style,
        fontSize=table_font_size,
        leading=table_leading,
    )
    data = [[Paragraph(_clean_inline(cell), table_body_style) for cell in row] for row in normalized]
    table = Table(data, colWidths=col_widths, repeatRows=1)
    style_commands = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e3ebf3")),
        ("LINEBELOW", (0, 0), (-1, 0), 0.65, colors.HexColor("#7f95a8")),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#b8c4cf")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTNAME", (0, 0), (-1, 0), header_font),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]
    for row_index in range(2, len(data), 2):
        style_commands.append(("BACKGROUND", (0, row_index), (-1, row_index), colors.HexColor("#f7f9fb")))
    table.setStyle(TableStyle(style_commands))
    return table


def build_pdf(
    markdown_path: str | Path,
    output_path: str | Path,
    title: str = "UK Space-Based Solar Power Cost-Condition Map",
    cjk: bool = False,
) -> None:
    markdown_path = Path(markdown_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    font_name = _register_cjk_font() if cjk else "Helvetica"
    bold_font_name = font_name if cjk else "Helvetica-Bold"
    word_wrap = "CJK" if cjk else None

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="SmallBody", parent=styles["BodyText"], fontSize=8.5, leading=11, fontName=font_name, wordWrap=word_wrap))
    styles.add(ParagraphStyle(name="BulletSmall", parent=styles["BodyText"], fontSize=8.5, leading=11, leftIndent=12, bulletIndent=4, fontName=font_name, wordWrap=word_wrap))
    styles.add(ParagraphStyle(name="Caption", parent=styles["BodyText"], fontSize=8, leading=10, textColor=colors.HexColor("#3f4d5a"), fontName=font_name, wordWrap=word_wrap))
    styles.add(ParagraphStyle(name="ReportMeta", parent=styles["BodyText"], fontSize=9, leading=12, textColor=colors.HexColor("#34495e"), fontName=font_name, wordWrap=word_wrap))
    styles.add(ParagraphStyle(name="TableTitle", parent=styles["BodyText"], fontSize=9, leading=11, fontName=bold_font_name, textColor=colors.HexColor("#243447"), spaceBefore=6, spaceAfter=4, wordWrap=word_wrap))
    for style_name in ("Title", "Heading1", "Heading2", "Heading3", "BodyText"):
        styles[style_name].fontName = font_name
        styles[style_name].wordWrap = word_wrap
    styles["Title"].fontSize = 20
    styles["Title"].leading = 24
    styles["Heading1"].fontSize = 15
    styles["Heading1"].leading = 18
    styles["Heading1"].keepWithNext = 1
    styles["Heading2"].fontSize = 11.5
    styles["Heading2"].leading = 14
    styles["Heading2"].keepWithNext = 1
    styles["Heading3"].fontSize = 10.5
    styles["Heading3"].leading = 13

    story = []
    paragraph_buffer: list[str] = []
    table_buffer: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph_buffer
        if paragraph_buffer:
            story.append(Paragraph(_clean_inline(" ".join(paragraph_buffer)), styles["SmallBody"]))
            story.append(Spacer(1, 0.07 * inch))
            paragraph_buffer = []

    def flush_table() -> None:
        nonlocal table_buffer
        if table_buffer:
            table = _table_from_lines(table_buffer, styles["SmallBody"], max_width=7.15 * inch, header_font=bold_font_name)
            if table is not None:
                story.append(table)
                story.append(Spacer(1, 0.12 * inch))
            table_buffer = []

    for raw_line in markdown_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if line.startswith("|"):
            flush_paragraph()
            table_buffer.append(line)
            continue
        flush_table()
        if not line:
            flush_paragraph()
            continue
        if line.strip() in {"[[PAGEBREAK]]", "<!-- PAGEBREAK -->"}:
            flush_paragraph()
            story.append(PageBreak())
            continue
        if line.startswith("# "):
            flush_paragraph()
            story.append(Paragraph(_clean_inline(line[2:]), styles["Title"]))
            story.append(Spacer(1, 0.18 * inch))
        elif line.startswith("## "):
            flush_paragraph()
            heading_text = line[3:]
            if heading_text.startswith("One-way thresholds quantify"):
                minimum_following_space = 5.5
            elif heading_text.startswith("单变量阈值说明"):
                minimum_following_space = 4.25
            else:
                minimum_following_space = 2.75 if re.match(r"[678]\.\s", heading_text) else 2.0
            story.append(CondPageBreak(minimum_following_space * inch))
            story.append(Spacer(1, 0.12 * inch))
            story.append(Paragraph(_clean_inline(heading_text), styles["Heading1"]))
        elif line.startswith("### "):
            flush_paragraph()
            story.append(Paragraph(_clean_inline(line[4:]), styles["Heading2"]))
        elif line.startswith("!["):
            flush_paragraph()
            match = re.match(r"!\[(?P<caption>.*)\]\((?P<path>.*)\)", line)
            if match:
                image_path = (markdown_path.parent / match.group("path")).resolve()
                if image_path.exists():
                    image_heading = Paragraph(_clean_inline(match.group("caption")), styles["Heading2"])
                    img = Image(str(image_path))
                    max_width = 6.6 * inch
                    max_height = 4.6 * inch
                    scale = min(max_width / img.imageWidth, max_height / img.imageHeight)
                    img.drawWidth = img.imageWidth * scale
                    img.drawHeight = img.imageHeight * scale
                    story.append(KeepTogether([Spacer(1, 0.08 * inch), image_heading, img]))
                    story.append(Spacer(1, 0.08 * inch))
        elif line.startswith("- "):
            flush_paragraph()
            story.append(Paragraph(_clean_inline(line[2:]), styles["BulletSmall"], bulletText="-"))
        elif (
            line.startswith("Table ")
            or line.startswith("Appendix Table ")
            or line.startswith("表")
            or line.startswith("附录表")
        ):
            flush_paragraph()
            story.append(Paragraph(_clean_inline(line), styles["TableTitle"]))
        elif (
            line.startswith("Report subtitle:")
            or line.startswith("Author:")
            or line.startswith("Report date:")
            or line.startswith("Evidence reviewed through:")
            or line.startswith("Repository:")
            or line.startswith("Interactive model:")
            or line.startswith("Recommended citation:")
            or line.startswith("Evidence status:")
            or line.startswith("Version:")
            or line.startswith("Prepared as:")
            or line.startswith("Disclaimer:")
            or line.startswith("副标题：")
            or line.startswith("作者：")
            or line.startswith("报告日期：")
            or line.startswith("证据截止日期：")
            or line.startswith("项目仓库：")
            or line.startswith("交互模型：")
            or line.startswith("建议引用：")
            or line.startswith("证据状态：")
            or line.startswith("版本号：")
            or line.startswith("说明：")
            or line.startswith("免责声明：")
        ):
            flush_paragraph()
            story.append(Paragraph(_clean_inline(line), styles["ReportMeta"]))
            story.append(Spacer(1, 0.04 * inch))
        else:
            paragraph_buffer.append(line)
    flush_paragraph()
    flush_table()

    doc = _ReportDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=0.55 * inch,
        rightMargin=0.55 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
        title=title,
        author="Wenyu Gao",
        subject="Reproducible bilingual UK SBSP cost-condition threshold assessment",
        keywords="space-based solar power, SBSP, LCOE, threshold analysis, United Kingdom",
    )
    def _draw_later_page(canvas, doc_obj) -> None:
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#d7dde5"))
        canvas.setLineWidth(0.4)
        canvas.line(0.55 * inch, A4[1] - 0.38 * inch, A4[0] - 0.55 * inch, A4[1] - 0.38 * inch)
        canvas.setFont(font_name, 7)
        canvas.setFillColor(colors.HexColor("#5d6d7e"))
        canvas.drawString(0.55 * inch, A4[1] - 0.30 * inch, title)
        page_label = f"第 {doc_obj.page} 页" if cjk else f"Page {doc_obj.page}"
        canvas.drawRightString(A4[0] - 0.55 * inch, 0.30 * inch, page_label)
        canvas.restoreState()

    def _draw_first_page(canvas, doc_obj) -> None:
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#2f5d7c"))
        canvas.setLineWidth(1.2)
        canvas.line(0.55 * inch, A4[1] - 0.62 * inch, A4[0] - 0.55 * inch, A4[1] - 0.62 * inch)
        canvas.setFont(font_name, 7)
        canvas.setFillColor(colors.HexColor("#5d6d7e"))
        page_label = f"第 {doc_obj.page} 页" if cjk else f"Page {doc_obj.page}"
        canvas.drawRightString(A4[0] - 0.55 * inch, 0.30 * inch, page_label)
        canvas.restoreState()

    doc.build(story, onFirstPage=_draw_first_page, onLaterPages=_draw_later_page)


if __name__ == "__main__":
    build_pdf("report/final_report.md", "report/final_report.pdf")
