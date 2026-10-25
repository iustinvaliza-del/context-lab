# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "pymupdf>=1.24.3",
# ]
# ///
"""Read an IESE case PDF for prep: page text, exhibit tables as markdown, and page images.

Plain PyMuPDF text extraction turns an exhibit table into a column of loose values and returns
nothing for a scanned page. This module prints each page's text, then each table on that page as
a markdown table, then the path of a PNG of the page when it has a table or very little text, so
the numbers can be checked against the image with the Read tool.

How tables are found on each page:
1. A page whose text runs sideways (a landscape exhibit printed on a portrait page) is redrawn
   upright on an in-memory page first. The PDF file is never changed.
2. PyMuPDF's default find_tables() strategy, which follows ruling lines.
3. Only if that keeps nothing: strategy="text" for borderless tables, clipped to the rows that look
   like table rows. On a whole page the text strategy also builds columns out of the prose and the
   sideways licence watermark in the margin, and cuts numbers apart ("-1.00" read as "-1.0" | "0").

Usage:
    uv run read_case.py <pdf> [<pdf> ...] [--out <dir>]
    from read_case import read_case, format_case

Page images go to <out>/<pdf stem>/p<N>.png; the default <out> is <system temp>/case-pages.
Requires PyMuPDF 1.24.3 or later (the pymupdf module name). Run it with `uv run read_case.py ...` and uv installs PyMuPDF from the header above.
"""
from __future__ import annotations

import argparse
import os
import re
import statistics
import sys
import tempfile
from typing import Any, Optional

import pymupdf as fitz  # the "fitz" name is deprecated in PyMuPDF

DPI = 170  # page images: small table digits stay legible
LOW_TEXT_CHARS = 500  # non-space characters; below this a page is likely scanned or an image exhibit
MIN_SIDEWAYS_CHARS = 300  # the margin licence watermark alone is about 150 sideways characters
LONG_PATH_CHARS = 248  # Windows MAX_PATH is 260 with the terminator, and 248 for folders
SEGMENT_GAP = 0.8  # a gap wider than this many word heights separates two cells of a row
ROW_GAP = 2.5  # table rows further apart than this many row heights start a new table
MAX_HEADER_ROWS = 3  # rows without numbers taken in above a run of numeric rows
SHORT_CELL_CHARS = 40  # a cell this short can be a data cell; a longer one is prose
TURN_ANGLE = {(0, -1): 270, (0, 1): 90, (-1, 0): 180}  # text direction -> show_pdf_page rotate
NUMBER = re.compile(r"^[(]?[-+−–]?[$€£]?\d[\d,.]*(%|[kmb]n?|x)?[)]?$", re.IGNORECASE)
CAPTION = re.compile(r"^(exhibit|table|figure)$", re.IGNORECASE)
BACKSLASH = chr(92)

_quiet_layout_hint = getattr(fitz, "no_recommend_layout", None)
if _quiet_layout_hint is not None:
    _quiet_layout_hint()  # PyMuPDF 1.26+ prints a one-time install hint to stdout from find_tables()


def read_case(pdf_path: str, out_dir: Optional[str] = None) -> dict[str, Any]:
    """Read a case PDF: page text, tables as rows of cells, and PNGs of the pages worth checking.

    Args:
        pdf_path: path to the case PDF. Paths past the Windows 260-character limit work.
        out_dir: folder for page images; each PDF gets a subfolder named after its file stem.
            Default: <system temp>/case-pages. Keep it out of the course folders.

    Returns:
        {"pdf": absolute path, "image_dir": folder of this PDF's PNGs,
         "pages": [{"page": 1-based number, "text": page text, "chars": non-space characters,
                    "turned": degrees the page was turned to read it (0 if upright),
                    "tables": [{"strategy": "lines" or "text", "rows": [[cell, ...], ...]}],
                    "image": PNG path or None, "image_reason": "table", "little text" or None}]}

    Raises:
        RuntimeError: the installed PyMuPDF has no find_tables (older than 1.23).
        FileNotFoundError: the PDF does not exist.
        fitz.FileDataError: the file is not a readable PDF.
    """
    if not hasattr(fitz.Page, "find_tables"):
        raise RuntimeError(f"PyMuPDF {fitz.VersionBind} has no find_tables; 1.23 or later is needed")
    pdf = os.path.abspath(pdf_path)
    base = out_dir if out_dir is not None else os.path.join(tempfile.gettempdir(), "case-pages")
    image_dir = os.path.join(os.path.abspath(base), os.path.splitext(os.path.basename(pdf))[0])
    doc = _open_pdf(pdf)
    try:
        pages = [_read_page(page, image_dir) for page in doc]
    finally:
        doc.close()
    return {"pdf": pdf, "image_dir": image_dir, "pages": pages}


def format_case(result: dict[str, Any]) -> str:
    """Render read_case() output as text: page markers, page text, markdown tables, PNG paths.

    Args:
        result: the dict read_case() returned.

    Returns:
        The printable report.
    """
    out = [f"# {os.path.basename(result['pdf'])} ({len(result['pages'])} pages)",
           f"Page images folder: {result['image_dir']}"]
    count = 0
    for page in result["pages"]:
        number = page["page"]
        out.append(f"\n===== Page {number} =====")
        if page["turned"]:
            out.append("(Printed sideways: its tables were read, and its image drawn, turned upright.)")
        out.append(page["text"].rstrip())
        for table in page["tables"]:
            count += 1
            rows = table["rows"]
            out.append(f"\n[Table {count}, page {number}: {table['strategy']} strategy, "
                       f"{len(rows)} rows x {len(rows[0])} columns]")
            out.append(_markdown(rows))
        if page["image"]:
            why = ("check the table numbers against it" if page["image_reason"] == "table" else
                   f"only {page['chars']} characters of text, likely scanned or an image exhibit")
            out.append(f"\n[Page {number} image: {why}] {page['image']}")
    return "\n".join(out)


def _win_path(path: str) -> str:
    """Absolute path; past the Windows length limit, the long-path prefixed form open() accepts."""
    full = os.path.abspath(path)
    prefix = BACKSLASH + BACKSLASH + "?" + BACKSLASH
    if os.name == "nt" and len(full) >= LONG_PATH_CHARS and not full.startswith(prefix):
        return prefix + full
    return full


def _open_pdf(path: str) -> fitz.Document:
    """Open a PDF from its bytes, so a path longer than the Windows limit still opens."""
    with open(_win_path(path), "rb") as handle:
        data = handle.read()
    return fitz.open(stream=data, filetype="pdf")


def _read_page(page: fitz.Page, image_dir: str) -> dict[str, Any]:
    """Text, tables and, when useful, a PNG for one page."""
    text = page.get_text()
    chars = len("".join(text.split()))
    work, turned, holder = _upright(page)
    try:
        tables = _find_tables(work)
        reason = "table" if tables else ("little text" if chars < LOW_TEXT_CHARS else None)
        image = None
        if reason:
            image = os.path.join(image_dir, f"p{page.number + 1}.png")
            _save_png(work, image)
    finally:
        if holder is not None:
            holder.close()
    return {"page": page.number + 1, "text": text, "chars": chars, "turned": turned,
            "tables": tables, "image": image, "image_reason": reason}


def _upright(page: fitz.Page) -> tuple[fitz.Page, int, Optional[fitz.Document]]:
    """Return the page with its text running left to right, the turn applied, and its holder doc.

    Case PDFs print landscape exhibits sideways on portrait pages, and the table strategies then
    read columns as rows. Such a page is drawn upright onto a new in-memory page. A page is turned
    only when most of its text runs one sideways direction and there is clearly more of it than
    the margin watermark, so a scanned page carrying only the watermark is left as it is.
    """
    chars: dict[tuple[int, int], int] = {}
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            key = (round(line["dir"][0]), round(line["dir"][1]))
            chars[key] = chars.get(key, 0) + sum(len(span["text"].strip()) for span in line["spans"])
    horizontal = chars.pop((1, 0), 0)
    if not chars:
        return page, 0, None
    direction, count = max(chars.items(), key=lambda item: item[1])
    if direction not in TURN_ANGLE or count <= horizontal or count < MIN_SIDEWAYS_CHARS:
        return page, 0, None
    angle = TURN_ANGLE[direction]
    width, height = page.rect.width, page.rect.height
    if angle != 180:
        width, height = height, width
    holder = fitz.open()
    turned = holder.new_page(width=width, height=height)
    turned.show_pdf_page(turned.rect, page.parent, page.number, rotate=angle)
    return turned, angle, holder


def _find_tables(page: fitz.Page) -> list[dict[str, Any]]:
    """Tables on an upright page: ruled tables first, borderless ones only if none were kept.

    Each table is extracted right after its own find_tables() call, because Table.extract() reads
    the characters of the most recent find_tables() call (a module-level list in pymupdf.table).
    """
    kept = []
    for table in page.find_tables().tables:
        grid = _clean(table.extract())
        if _is_data_table(grid):
            kept.append({"strategy": "lines", "rows": grid})
    if kept:
        return kept
    for clip in _table_regions(_rows(page)):
        for table in page.find_tables(clip=clip, strategy="text").tables:
            _widen_outer_columns(table, clip)
            grid = _clean(table.extract())
            if _is_data_table(grid):
                kept.append({"strategy": "text", "rows": grid})
    return kept


def _rows(page: fitz.Page) -> list[dict[str, Any]]:
    """Group the page's left-to-right words into visual rows, each split into cells at wide gaps."""
    textpage = page.get_textpage()
    sideways = [fitz.Rect(line["bbox"])
                for block in page.get_text("dict", textpage=textpage)["blocks"]
                for line in block.get("lines", []) if abs(line["dir"][1]) > 0.01]
    words = []
    for word in page.get_text("words", textpage=textpage):
        rect = fitz.Rect(word[:4])
        if not any((rect.tl + rect.br) / 2 in box for box in sideways):  # drops the watermark
            words.append((rect, word[4]))
    words.sort(key=lambda item: ((item[0].y0 + item[0].y1) / 2, item[0].x0))
    grouped: list[list[tuple[fitz.Rect, str]]] = []
    for rect, text in words:
        anchor = grouped[-1][0][0] if grouped else None
        if anchor is not None and abs((rect.y0 + rect.y1) - (anchor.y0 + anchor.y1)) / 2 <= rect.height / 2:
            grouped[-1].append((rect, text))
        else:
            grouped.append([(rect, text)])
    rows = []
    for row in grouped:
        row.sort(key=lambda item: item[0].x0)
        height = statistics.median(rect.height for rect, _ in row)
        cells = [[row[0][1]]]
        box = fitz.Rect(row[0][0])
        for (previous, _), (rect, text) in zip(row, row[1:]):
            if rect.x0 - previous.x1 > SEGMENT_GAP * height:
                cells.append([text])
            else:
                cells[-1].append(text)
            box |= rect
        rows.append({"rect": box, "height": height, "cells": [" ".join(cell) for cell in cells]})
    return rows


def _table_regions(rows: list[dict[str, Any]]) -> list[fitz.Rect]:
    """Rectangles around runs of table-like rows, with the header rows just above each run.

    A row is table-like when at least two of its cells are numbers; prose has one long cell. Header
    rows ("A  B  C  D  E", "Metric  Year 1  Year 2") hold no numbers, so up to MAX_HEADER_ROWS rows
    of two or more cells directly above a run are taken in, stopping at an "Exhibit N" caption.
    """
    numeric = [i for i, row in enumerate(rows)
               if sum(all(NUMBER.match(word) for word in cell.split()) for cell in row["cells"]) >= 2]
    runs: list[list[int]] = []
    for i in numeric:
        if runs and rows[i]["rect"].y0 - rows[runs[-1][-1]]["rect"].y1 <= ROW_GAP * rows[i]["height"]:
            runs[-1].append(i)
        else:
            runs.append([i])
    regions = []
    for run in runs:
        first = run[0]
        while (first > 0 and run[0] - first < MAX_HEADER_ROWS
               and len(rows[first - 1]["cells"]) >= 2
               and not CAPTION.match(rows[first - 1]["cells"][0].split()[0])
               and rows[first]["rect"].y0 - rows[first - 1]["rect"].y1 <= ROW_GAP * rows[first]["height"]):
            first -= 1
        box = fitz.Rect(rows[first]["rect"])
        for row in rows[first + 1:run[-1] + 1]:
            box |= row["rect"]
        regions.append(box + (-2, -2, 2, 2))
    return regions


def _widen_outer_columns(table: Any, clip: fitz.Rect) -> None:
    """Stretch a text-strategy table's first and last columns out to the clip edges.

    The text strategy puts a table's outer edges at the words that line up, so a row label or
    header wider than the rest loses its outer part ("NPV at 10%" read as "10%", "2018" as "201").
    The clip was drawn around the table's own rows, so this only takes in characters of those rows;
    extract() still assigns every character by its centre, so none moves between inner cells.
    """
    left = min(cell[0] for cell in table.cells)
    right = max(cell[2] for cell in table.cells)
    table.cells = [(min(clip.x0, cell[0]) if cell[0] == left else cell[0], cell[1],
                    max(clip.x1, cell[2]) if cell[2] == right else cell[2], cell[3])
                   for cell in table.cells]


def _clean(rows: list[list[Optional[str]]]) -> list[list[str]]:
    """Turn None into "", collapse whitespace, and drop rows and columns that are entirely empty."""
    grid = [[" ".join((cell or "").split()) for cell in row] for row in rows]
    grid = [row for row in grid if any(row)]
    width = max((len(row) for row in grid), default=0)
    keep = [j for j in range(width) if any(j < len(row) and row[j] for row in grid)]
    return [[row[j] if j < len(row) else "" for j in keep] for row in grid]


def _is_data_table(grid: list[list[str]]) -> bool:
    """Keep a table only if it looks like data rather than a paragraph caught in a frame.

    Rule, after empty rows and columns are dropped: at least two rows and two columns, and at least
    two rows holding two or more short cells (SHORT_CELL_CHARS or fewer). A one-column "table" is a
    paragraph or text box; a grid whose rows hold at most one short cell is prose split into
    columns. Exhibit rows hold several short cells: labels and numbers.
    """
    if len(grid) < 2 or len(grid[0]) < 2:
        return False
    short_rows = sum(1 for row in grid
                     if sum(1 for cell in row if cell and len(cell) <= SHORT_CELL_CHARS) >= 2)
    return short_rows >= 2


def _markdown(rows: list[list[str]]) -> str:
    """Render rows as a markdown table; the first row is the header."""
    lines = []
    for index, row in enumerate(rows):
        lines.append("| " + " | ".join(cell.replace("|", BACKSLASH + "|") for cell in row) + " |")
        if index == 0:
            lines.append("|" + " --- |" * len(row))
    return "\n".join(lines)


def _save_png(page: fitz.Page, path: str) -> None:
    """Render the page at DPI and write it as a PNG, creating the folder; long paths are fine."""
    os.makedirs(_win_path(os.path.dirname(path)), exist_ok=True)
    with open(_win_path(path), "wb") as handle:
        handle.write(page.get_pixmap(dpi=DPI).tobytes("png"))


def main(argv: Optional[list[str]] = None) -> int:
    """CLI: print each PDF's pages, tables and image paths; return 1 if any PDF could not be read."""
    parser = argparse.ArgumentParser(description="Read case PDFs: page text, tables as markdown, page images.")
    parser.add_argument("pdfs", nargs="+", help="case PDF path(s)")
    parser.add_argument("--out", default=None, help="folder for page images (default: <temp>/case-pages)")
    args = parser.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # euro signs, curly quotes
    status = 0
    for path in args.pdfs:
        try:
            print(format_case(read_case(path, args.out)))
        except (OSError, RuntimeError, ValueError) as e:
            print(f"error: {path}: {e}", file=sys.stderr)
            status = 1
    return status


if __name__ == "__main__":
    sys.exit(main())
