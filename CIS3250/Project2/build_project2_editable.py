"""Create an editable Word version from the same report content as the PDF."""
from pathlib import Path
import runpy
import pandas as pd
from unittest.mock import patch
from html.parser import HTMLParser
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Image, PageBreak
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

BASE = Path(__file__).resolve().parent
captured = []
read_csv = pd.read_csv
def report_csv(path, *args, **kwargs):
    # The sorted weights file preserves the report's selected coefficient rows.
    if Path(path).name == "data_a_all_coefficients.csv":
        path = Path(path).with_name("data_a_standardized_feature_weights.csv")
    return read_csv(path, *args, **kwargs)
with patch.object(SimpleDocTemplate, "build", lambda self, story, **kwargs: captured.extend(story)), patch.object(pd, "read_csv", report_csv):
    runpy.run_path(str(BASE / "build_project2_report.py"))
doc = Document()
section = doc.sections[0]
section.page_width, section.page_height = Inches(8.5), Inches(11)
section.left_margin = section.right_margin = Pt(54)
section.top_margin = section.bottom_margin = Pt(48)
section.footer_distance = Pt(24)
for name in ["Normal", "Title", "Heading 1", "Heading 2", "Caption"]:
    style = doc.styles[name]
    style.font.name = "Times New Roman"
    style.font.color.rgb = RGBColor(0,0,0)
    for border in list(style.element.findall(".//" + qn("w:pBdr"))):
        border.getparent().remove(border)
    rfonts = style.element.get_or_add_rPr().rFonts
    if rfonts is not None:
        for attr in ["asciiTheme", "hAnsiTheme", "eastAsiaTheme", "cstheme"]:
            rfonts.attrib.pop(qn("w:" + attr), None)
normal = doc.styles["Normal"]
normal.font.size = Pt(11)
normal.paragraph_format.line_spacing = Pt(14.3)
normal.paragraph_format.space_after = Pt(8)
normal.paragraph_format.widow_control = True
for name, size in [("Title",13), ("Heading 1",11.5)]:
    s = doc.styles[name]
    s.font.size = Pt(size)
    s.font.bold = True
    s.paragraph_format.space_before = Pt(0 if name == "Title" else 5)
    s.paragraph_format.space_after = Pt(12 if name == "Title" else 8)
    s.paragraph_format.line_spacing = Pt(16 if name == "Title" else 14)
    s.paragraph_format.keep_with_next = True


class Runs(HTMLParser):
    def __init__(self, paragraph):
        super().__init__(convert_charrefs=True)
        self.paragraph = paragraph
        self.bold = self.italic = self.sup = 0
    def handle_starttag(self, tag, attrs):
        if tag in ["b", "strong"]: self.bold += 1
        elif tag in ["i", "em"]: self.italic += 1
        elif tag == "super": self.sup += 1
        elif tag == "br": self.paragraph.add_run().add_break()
    def handle_endtag(self, tag):
        if tag in ["b", "strong"]: self.bold = max(0, self.bold-1)
        elif tag in ["i", "em"]: self.italic = max(0, self.italic-1)
        elif tag == "super": self.sup = max(0,self.sup-1)
    def handle_data(self, data):
        r = self.paragraph.add_run(data)
        if self.bold: r.bold = True
        if self.italic: r.italic = True
        if self.sup: r.font.superscript = True


def add_text(paragraph, text):
    Runs(paragraph).feed(text)


for obj in captured:
    if isinstance(obj, PageBreak):
        doc.add_page_break()
    elif isinstance(obj, Paragraph):
        style = obj.style.name
        para = doc.add_paragraph(style="Title" if style == "TitleReport" else "Heading 1" if style == "HeadReport" else "Normal")
        add_text(para, obj.text)
        if style == "SmallReport":
            para.paragraph_format.line_spacing = Pt(11.5)
            para.paragraph_format.space_after = Pt(7)
            for r in para.runs: r.font.size = Pt(9)
    elif isinstance(obj, Table):
        rows = obj._cellvalues
        t = doc.add_table(rows=len(rows), cols=len(rows[0]))
        t.alignment = WD_TABLE_ALIGNMENT.LEFT
        t.autofit = False
        widths = obj._argW
        for j, width in enumerate(widths):
            t.columns[j].width = Pt(width)
        borders = OxmlElement("w:tblBorders")
        for edge in ["top", "left", "bottom", "right", "insideH", "insideV"]:
            el = OxmlElement("w:" + edge)
            el.set(qn("w:val"), "single")
            el.set(qn("w:sz"), "4")
            el.set(qn("w:color"), "D9D9D9")
            borders.append(el)
        t._tbl.tblPr.append(borders)
        for i, row in enumerate(rows):
            trpr = t.rows[i]._tr.get_or_add_trPr()
            no_split = OxmlElement("w:cantSplit")
            trpr.append(no_split)
            if i == 0:
                trpr.append(OxmlElement("w:tblHeader"))
            for j, value in enumerate(row):
                cell = t.cell(i,j)
                cell.width = Pt(widths[j])
                cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
                tcpr = cell._tc.get_or_add_tcPr()
                margins = OxmlElement("w:tcMar")
                for edge in ["top", "left", "bottom", "right"]:
                    el = OxmlElement("w:"+edge)
                    el.set(qn("w:w"), "70")
                    el.set(qn("w:type"), "dxa")
                    margins.append(el)
                tcpr.append(margins)
                if i == 0:
                    shading = OxmlElement("w:shd")
                    shading.set(qn("w:fill"), "F2F2F2")
                    tcpr.append(shading)
                p = cell.paragraphs[0]
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = Pt(11)
                if j > 0: p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                add_text(p, value.text if isinstance(value, Paragraph) else str(value))
                for r in p.runs: r.font.size = Pt(9)
        after = doc.add_paragraph()
        after.paragraph_format.space_after = Pt(0)
        after.paragraph_format.line_spacing = Pt(5)
        after.add_run().font.size = Pt(5)
    elif isinstance(obj, Image):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.line_spacing = 1
        p.add_run().add_picture(str(obj.filename), width=Pt(obj.drawWidth), height=Pt(obj.drawHeight))
footer = section.footer.paragraphs[0]
footer.paragraph_format.space_after = Pt(0)
footer.add_run("CIS3250 | Project 2 Results").font.size = Pt(9)
footer.add_run("\t")
footer.paragraph_format.tab_stops.add_tab_stop(Pt(490))
field = OxmlElement("w:fldSimple")
field.set(qn("w:instr"), "PAGE")
footer._p.append(field)
doc.core_properties.title = "CIS3250 Project 2 Results"
doc.core_properties.author = ""
target = BASE / "output" / "docx" / "CIS3250_Project2_Results_Editable.docx"
target.parent.mkdir(parents=True, exist_ok=True)
doc.save(target)
print(target)
