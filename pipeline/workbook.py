# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "openpyxl",
# ]
# ///
"""IESE case-workbook template and builder.

Conventions: IESE red / white / dove grey palette, Tahoma 8,
yellow input cells, Cover / Inputs / exhibit sheets / Checks.

CLI
    python workbook.py template                      # writes IESE_Case_Template.xltx next to this file
    python workbook.py new "<session folder>" "<Case name>" [--course "..."] [--session N] [--exhibit "Title" ...]
        # scaffolds <Case>_Exhibits.xlsx inside the session folder

Library
    from workbook import CaseWorkbook
    wb = CaseWorkbook(case="Baltran", course="Entrepreneurial Finance 1", session=4)
    wb.add_input("Sofina investment ($)", 2_800_000, source="Case p.3", kind="case fact")
    ws = wb.add_exhibit("Cap table two ways", caption="...")
    wb.add_check("Shares sum to total", "='1 Cap table'!B29", "='1 Cap table'!B24")
    wb.save(path)
"""
from __future__ import annotations

import argparse
import datetime as _dt
import os
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.worksheet import Worksheet

# ---------------------------------------------------------------- palette (IESE brand + input convention)
RED = "FF0000"        # IESE red (Brandfetch; syllabus headings)
GREY = "666666"       # IESE dove grey
GREY_LIGHT = "F2F2F2"
INPUT_YELLOW = "FFF2CC"   # every input or assumption cell
WHITE = "FFFFFF"
BLACK = "000000"

FONT_NAME = "Tahoma"
FONT_SIZE = 8

FMT_INT = '#,##0;(#,##0);"-"'
FMT_DEC = '#,##0.00;(#,##0.00);"-"'
FMT_PCT = '0.0%;(0.0%);"-"'
FMT_MULT = '0.00"x"'


def _font(bold=False, color=BLACK, italic=False, size=FONT_SIZE):
    return Font(name=FONT_NAME, size=size, bold=bold, italic=italic, color=color)


def _fill(hex_):
    return PatternFill("solid", fgColor=hex_)


THIN = Side(style="thin", color=GREY)
HAIR = Side(style="hair", color=GREY)

STYLE = {
    "title": dict(font=_font(bold=True, color=WHITE, size=11), fill=_fill(RED)),
    "subtitle": dict(font=_font(color=GREY)),
    "section": dict(font=_font(bold=True, color=WHITE), fill=_fill(RED)),
    "colhead": dict(font=_font(bold=True, color=GREY), border=Border(bottom=THIN)),
    "input": dict(fill=_fill(INPUT_YELLOW)),
    "result": dict(font=_font(bold=True, color=RED), border=Border(top=THIN, bottom=THIN)),
    "note": dict(font=_font(color=GREY, italic=True)),
    "formula_label": dict(font=_font(color=GREY)),
}


def style(cell, name):
    for k, v in STYLE[name].items():
        setattr(cell, k, v)
    return cell


def base_font(ws: Worksheet, max_row=200, max_col=12):
    for row in ws.iter_rows(min_row=1, max_row=max_row, max_col=max_col):
        for c in row:
            if c.font.name != FONT_NAME:
                # only cells already set in Tahoma (title bars) keep a larger size; Excel's Calibri default resets to 8
                color = c.font.color.rgb if c.font.color and isinstance(c.font.color.rgb, str) else BLACK
                c.font = _font(bold=c.font.bold, color=color, italic=c.font.italic)


def widths(ws: Worksheet, spec: dict[str, float]):
    for col, w in spec.items():
        ws.column_dimensions[col].width = w


# ---------------------------------------------------------------- the workbook
class CaseWorkbook:
    def __init__(self, case: str, course: str = "", session: int | str = "", author: str = "", questions: list[str] | None = None):
        self.case, self.course, self.session, self.author = case, course, session, author
        self.wb = Workbook()
        self.cover = self.wb.active
        self.cover.title = "Cover"
        self.inputs = self.wb.create_sheet("Inputs")
        self.checks = self.wb.create_sheet("Checks")
        self._exhibits: list[Worksheet] = []
        self._input_row = 5
        self._check_row = 5
        self._assumption_row = None
        self._build_cover(questions or [])
        self._build_inputs()
        self._build_checks()

    # ---- Cover
    def _build_cover(self, questions):
        ws = self.cover
        ws.sheet_view.showGridLines = False
        widths(ws, {"A": 3, "B": 26, "C": 70, "D": 18})
        for col in "BCD":
            style(ws[f"{col}2"], "title")
        ws["B2"] = f"{self.case}"
        ws["B3"] = f"{self.course}" + (f" · Session {self.session}" if self.session else "")
        style(ws["B3"], "subtitle")
        ws["B4"] = f"Prepared {_dt.date.today():%d %b %Y}" + (f" · {self.author}" if self.author else "")
        style(ws["B4"], "subtitle")

        ws["B6"] = "How to read this workbook"
        style(ws["B6"], "section"); style(ws["C6"], "section"); style(ws["D6"], "section")
        rows = [
            ("Yellow cells", "Inputs and assumptions. Everything not yellow is a formula. Change a yellow cell and every exhibit updates."),
            ("Red bold cells", "Results cited in the report."),
            ("Grey text", "Formula descriptions and notes; source references next to each input."),
            ("Inputs sheet", "One row per input: value, unit, source (case page or 'assumption'), and kind."),
            ("Checks sheet", "Identities that must hold (sums, reconciliations). Every row must read OK before numbers leave this file."),
        ]
        r = 7
        for k, v in rows:
            ws[f"B{r}"] = k; style(ws[f"B{r}"], "formula_label"); ws[f"B{r}"].alignment = Alignment(vertical="top")
            ws[f"C{r}"] = v; ws[f"C{r}"].alignment = Alignment(vertical="top")
            r += 1

        r += 1
        ws[f"B{r}"] = "Case questions"
        for col in "BCD": style(ws[f"{col}{r}"], "section")
        r += 1
        if not questions:
            questions = ["(paste the syllabus questions here, one per row)"]
        for i, q in enumerate(questions, 1):
            ws[f"B{r}"] = f"Q{i}"; style(ws[f"B{r}"], "formula_label")
            ws[f"C{r}"] = q; ws[f"C{r}"].alignment = Alignment(wrap_text=True, vertical="top")
            r += 1

        r += 1
        ws[f"B{r}"] = "Assumptions log"
        for col in "BCD": style(ws[f"{col}{r}"], "section")
        r += 1
        for col, h in zip("BCD", ("Assumption", "Why / effect", "Your decision")):
            ws[f"{col}{r}"] = h; style(ws[f"{col}{r}"], "colhead")
        self._assumption_row = r + 1
        for i in range(3):
            for col in "BCD":
                style(ws[f"{col}{self._assumption_row + i}"], "input")
        base_font(ws)

    def add_assumption(self, text: str, why: str = "", decision: str = ""):
        r = self._assumption_row
        while self.cover[f"B{r}"].value:
            r += 1
        self.cover[f"B{r}"] = text; self.cover[f"C{r}"] = why; self.cover[f"D{r}"] = decision
        for col in "BCD":
            style(self.cover[f"{col}{r}"], "input")
            self.cover[f"{col}{r}"].font = _font()
            self.cover[f"{col}{r}"].alignment = Alignment(wrap_text=True, vertical="top")

    # ---- Inputs
    def _build_inputs(self):
        ws = self.inputs
        ws.sheet_view.showGridLines = False
        widths(ws, {"A": 3, "B": 44, "C": 16, "D": 10, "E": 26, "F": 14})
        for col in "BCDEF":
            style(ws[f"{col}2"], "title")
        ws["B2"] = "Inputs"
        ws["B3"] = "Yellow = input. Source names the case page, exhibit, or 'assumption'. Formulas elsewhere reference column C by absolute address."
        style(ws["B3"], "note")
        for col, h in zip("BCDEF", ("Input", "Value", "Unit", "Source", "Kind")):
            ws[f"{col}4"] = h; style(ws[f"{col}4"], "colhead")
        base_font(ws)

    def add_input(self, name: str, value, unit: str = "", source: str = "", kind: str = "case fact", fmt: str | None = None) -> str:
        """Add one input row; returns the absolute reference (e.g. Inputs!$C$5) for formulas."""
        r = self._input_row
        ws = self.inputs
        ws[f"B{r}"] = name
        ws[f"C{r}"] = value; style(ws[f"C{r}"], "input")
        if fmt: ws[f"C{r}"].number_format = fmt
        elif isinstance(value, float) and abs(value) < 1: ws[f"C{r}"].number_format = FMT_PCT
        elif isinstance(value, (int, float)): ws[f"C{r}"].number_format = FMT_INT if float(value).is_integer() else FMT_DEC
        ws[f"D{r}"] = unit; ws[f"E{r}"] = source; ws[f"F{r}"] = kind
        for col in "BDEF":
            ws[f"{col}{r}"].font = _font(color=GREY if col != "B" else BLACK)
        if kind.lower().startswith("assum"):
            ws[f"F{r}"].font = _font(bold=True, color=RED)
        ws[f"C{r}"].font = _font()
        self._input_row += 1
        return f"Inputs!$C${r}"

    # ---- Exhibits
    def add_exhibit(self, title: str, caption: str = "", headers: list[str] | None = None) -> Worksheet:
        n = len(self._exhibits) + 1
        ws = self.wb.create_sheet(f"{n} {title}"[:31], index=2 + len(self._exhibits))
        ws.sheet_view.showGridLines = False
        widths(ws, {"A": 3, "B": 46, "C": 34, "D": 16, "E": 16, "F": 16, "G": 16})
        for col in "BCDEFG":
            style(ws[f"{col}2"], "title")
        ws["B2"] = f"Exhibit {n} · {title}"
        ws["B3"] = caption; style(ws["B3"], "note")
        if headers:
            for i, h in enumerate(headers):
                c = ws.cell(row=5, column=2 + i, value=h); style(c, "colhead")
                if i >= 2: c.alignment = Alignment(horizontal="right")
        ws._next_row = 6 if headers else 5  # noqa: private scratch attribute for the row cursor
        self._exhibits.append(ws)
        return ws

    @staticmethod
    def row(ws: Worksheet, label: str, formula_text: str = "", *values, result=False, fmt=FMT_INT):
        r = ws._next_row
        ws.cell(row=r, column=2, value=label).font = _font(bold=result, color=RED if result else BLACK)
        c = ws.cell(row=r, column=3, value=formula_text); style(c, "formula_label")
        for i, v in enumerate(values):
            cell = ws.cell(row=r, column=4 + i, value=v)
            cell.number_format = fmt; cell.alignment = Alignment(horizontal="right")
            cell.font = _font(bold=result, color=RED if result else BLACK)
            if result: cell.border = Border(top=THIN, bottom=THIN)
        if result:
            ws.cell(row=r, column=2).border = Border(top=THIN, bottom=THIN)
            ws.cell(row=r, column=3).border = Border(top=THIN, bottom=THIN)
        ws._next_row = r + 1
        return r

    @staticmethod
    def blank(ws: Worksheet, n=1):
        ws._next_row += n

    @staticmethod
    def note(ws: Worksheet, text: str):
        r = ws._next_row
        c = ws.cell(row=r, column=2, value=text); style(c, "note")
        ws._next_row = r + 1

    # ---- Checks
    def _build_checks(self):
        ws = self.checks
        ws.sheet_view.showGridLines = False
        widths(ws, {"A": 3, "B": 44, "C": 18, "D": 18, "E": 10})
        for col in "BCDE":
            style(ws[f"{col}2"], "title")
        ws["B2"] = "Checks"
        ws["B3"] = "Every row must read OK before any number is cited. Tolerance 0.5 in the last unit."
        style(ws["B3"], "note")
        for col, h in zip("BCDE", ("Check", "Expected", "Actual", "Status")):
            ws[f"{col}4"] = h; style(ws[f"{col}4"], "colhead")
        ws["B30"] = "All checks"; style(ws["B30"], "result")
        ws["E30"] = '=IF(COUNTIF(E5:E29,"FAIL")=0,"OK","FAIL")'; style(ws["E30"], "result")
        base_font(ws)

    def add_check(self, name: str, expected, actual, fmt=FMT_INT):
        r = self._check_row
        ws = self.checks
        ws[f"B{r}"] = name; ws[f"B{r}"].font = _font()
        ws[f"C{r}"] = expected; ws[f"D{r}"] = actual
        for col in "CD":
            ws[f"{col}{r}"].number_format = fmt; ws[f"{col}{r}"].font = _font()
        ws[f"E{r}"] = f'=IF(ABS(C{r}-D{r})<=0.5,"OK","FAIL")'
        ws[f"E{r}"].font = _font(bold=True)
        self._check_row += 1

    # ---- save
    def save(self, path: str, template: bool = False):
        self.wb.template = template
        for ws in self.wb.worksheets:
            ws.sheet_properties.tabColor = RED if ws.title in ("Cover",) else GREY
            ws.page_setup.orientation = "landscape"
            ws.sheet_properties.pageSetUpPr.fitToPage = True  # fitToWidth is ignored without this flag
            ws.page_setup.fitToWidth = 1
            ws.page_setup.fitToHeight = 0
            ws.print_options.horizontalCentered = False
        self.wb.save(path)
        return path


# ---------------------------------------------------------------- CLI
def _write_template(out_dir: str) -> str:
    wb = CaseWorkbook(case="<Case name>", course="<Course> ", session="<N>")
    wb.add_input("<input name>", 0, unit="$", source="Case p.<n>", kind="case fact")
    wb.add_input("<assumption name>", 0.0, unit="%", source="assumption", kind="assumption")
    ws = wb.add_exhibit("<Exhibit title>", caption="<what this exhibit shows and which report figures it backs>", headers=["Step", "Formula", "Case A", "Case B"])
    CaseWorkbook.row(ws, "<line item>", "<formula in words>", "=Inputs!$C$5", "=Inputs!$C$5")
    CaseWorkbook.row(ws, "<result line>", "<formula in words>", "=D6*2", "=E6*2", result=True)
    wb.add_check("<identity that must hold>", "=D6", "=D6")
    wb.add_assumption("<assumption>", "<why it is needed and what it changes>", "<your decision, date>")
    path = os.path.join(out_dir, "IESE_Case_Template.xltx")
    return wb.save(path, template=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("template", help="write IESE_Case_Template.xltx next to this script")
    new = sub.add_parser("new", help="scaffold <Case>_Exhibits.xlsx in a session folder")
    new.add_argument("session_dir"); new.add_argument("case")
    new.add_argument("--course", default=""); new.add_argument("--session", default="")
    new.add_argument("--exhibit", action="append", default=[], help="exhibit title (repeatable)")
    new.add_argument("--question", action="append", default=[], help="case question (repeatable)")
    a = ap.parse_args(argv)
    here = os.path.dirname(os.path.abspath(__file__))
    if a.cmd == "template":
        print(_write_template(here))
    else:
        wb = CaseWorkbook(case=a.case, course=a.course, session=a.session, questions=a.question)
        for t in a.exhibit or ["Exhibit"]:
            wb.add_exhibit(t, headers=["Step", "Formula", "Value"])
        safe = "".join(ch for ch in a.case if ch.isalnum() or ch in " _-").strip().replace(" ", "_")
        print(wb.save(os.path.join(a.session_dir, f"{safe}_Exhibits.xlsx")))


if __name__ == "__main__":
    main()
