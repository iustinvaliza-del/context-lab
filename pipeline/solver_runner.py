"""Drive Excel's own Solver from Python for IESE case workbooks.

A case's `_build` script lays the model out on a sheet (with workbook.py) and describes it as a
SolverModel. This module sets the model up with Solver's own calls, solves it, keeps the Sensitivity
Report inside the workbook, and checks that the saved file re-solves on its own in a fresh Excel.

Pitfalls found on 2026-09-18 (Media Moguls) and handled here once:
- An automation Excel starts with no add-ins: open <LibraryPath>/SOLVER/SOLVER.XLAM, then call the
  Solver.xlam! functions through Application.Run. Auto_open is not needed.
- Solver keeps its model in the sheet only when Excel itself saves after the set-up; openpyxl cannot
  write it. So set up, solve and save inside one excel_session.
- pywin32 late binding sends Worksheet.Move(After=x) to Excel with no arguments, which moves the sheet
  into a new unsaved workbook. Reports are therefore placed with a positional Before.
- Solver names report rows after the nearest text to the left of each cell and the header above it:
  keep explanations to the right of the model.

Usage from a case build script:
    from solver_runner import SolverModel, excel_session, reopen_check, setup, solve
    model = SolverModel(sheet="1 Base LP", objective="$L$14", changing="$D$8:$K$8",
                        constraints=[("$L$11:$L$13", ">=", "$N$11:$N$13"), ("$D$8", "<=", "$D$16")])
    with excel_session(path) as (xl, book):
        setup(xl, book, model)
        result = solve(xl, book, model, report_before="Checks")
        book.Save()
    reopen_check(path, [model])
"""
from __future__ import annotations

import os
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Iterator

RELATIONS = {"<=": 1, "=": 2, ">=": 3, "int": 4, "bin": 5, "dif": 6}
ENGINES = {"grg": (1, "GRG Nonlinear"), "simplex": (2, "Simplex LP"), "evolutionary": (3, "Evolutionary")}
SENSES = {"max": 1, "min": 2, "value": 3}
OK_CODES = (0, 1)   # 0: optimal, all constraints hold; 1: GRG converged


@dataclass
class SolverModel:
    """One Solver model on one sheet. Cell addresses are absolute, e.g. "$L$14"."""
    sheet: str
    objective: str
    changing: str
    constraints: list[tuple[str, str, str]] = field(default_factory=list)   # (cell, relation, cell); rhs "" for int/bin/dif
    sense: str = "max"
    engine: str = "simplex"
    value_of: float = 0.0
    non_negative: bool = True


@dataclass
class SolveResult:
    code: int
    objective: float
    values: list[float]
    report_rows: list[tuple] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.code in OK_CODES


@contextmanager
def excel_session(path: str) -> Iterator[tuple[Any, Any]]:
    """Hidden Excel with Solver loaded and the workbook open. Closes without saving: call book.Save() yourself."""
    import win32com.client as win32

    xl = win32.DispatchEx("Excel.Application")
    xl.Visible = False
    xl.DisplayAlerts = False
    try:
        xl.Workbooks.Open(os.path.join(xl.LibraryPath, "SOLVER", "SOLVER.XLAM"))
        book = xl.Workbooks.Open(os.path.abspath(path))
        try:
            yield xl, book
        finally:
            book.Close(False)
    finally:
        xl.Quit()


def _run(xl: Any, name: str, *args: Any) -> Any:
    return xl.Run(f"Solver.xlam!{name}", *args)


def _flat(value: Any) -> list[Any]:
    if isinstance(value, tuple):
        return [v for row in value for v in (row if isinstance(row, tuple) else (row,))]
    return [value]


def cell(book: Any, ref: str) -> Any:
    """Range for a reference like "Inputs!$C$23" or "'1 Base LP'!$D$8"."""
    sheet, address = ref.rsplit("!", 1)
    return book.Worksheets(sheet.strip("'")).Range(address)


def setup(xl: Any, book: Any, model: SolverModel) -> None:
    """Store the model on its sheet, replacing any model already there."""
    ws = book.Worksheets(model.sheet)
    ws.Activate()
    engine_code, engine_name = ENGINES[model.engine]
    _run(xl, "SolverReset")
    _run(xl, "SolverOk", model.objective, SENSES[model.sense], model.value_of, model.changing, engine_code, engine_name)
    for lhs, relation, rhs in model.constraints:
        if relation in ("int", "bin", "dif"):
            _run(xl, "SolverAdd", lhs, RELATIONS[relation])
        else:
            _run(xl, "SolverAdd", lhs, RELATIONS[relation], rhs)
    ws.Names.Add("solver_neg", "=1" if model.non_negative else "=2", False)


def solve(xl: Any, book: Any, model: SolverModel, report_before: str | None = None) -> SolveResult:
    """Solve the model stored on its sheet and keep the solution.

    With report_before set, Solver also writes its Sensitivity Report, which is placed before that sheet
    and returned as rows (empty rows dropped).
    """
    ws = book.Worksheets(model.sheet)
    ws.Activate()
    before = {s.Name for s in book.Worksheets}
    code = _run(xl, "SolverSolve", True)
    if report_before:
        _run(xl, "SolverFinish", 1, [2])
    else:
        _run(xl, "SolverFinish", 1)
    xl.CalculateFull()
    rows: list[tuple] = []
    if report_before:
        new = [s for s in book.Worksheets if s.Name not in before]
        if not new:
            raise RuntimeError("Solver did not create a Sensitivity Report (is the engine Simplex LP or GRG?)")
        report = new[0]
        report.Move(book.Worksheets(report_before))
        rows = [r for r in report.UsedRange.Value if any(v not in (None, "") for v in r)]
    return SolveResult(code, ws.Range(model.objective).Value, _flat(ws.Range(model.changing).Value), rows)


def report_value(rows: list[tuple], address: str, column: str = "shadow") -> float:
    """Read one number from a Sensitivity Report row, found by its cell address (e.g. "$L$11").

    column: "final", "shadow" (shadow price, or reduced cost for a changing cell), "coefficient"
    (objective coefficient or constraint right-hand side), "increase", "decrease".
    """
    offset = {"final": 2, "shadow": 3, "coefficient": 4, "increase": 5, "decrease": 6}[column]
    for row in rows:
        values = list(row)
        if address in values:
            return values[values.index(address) + offset]
    raise KeyError(f"{address} not in the Sensitivity Report")


def reopen_check(path: str, models: list[SolverModel]) -> list[SolveResult]:
    """Reopen the saved file in a fresh Excel, zero each model's changing cells and re-solve with the saved
    model (no set-up calls). Nothing is saved. Proves the model travels with the file."""
    results = []
    with excel_session(path) as (xl, book):
        for model in models:
            ws = book.Worksheets(model.sheet)
            ws.Activate()
            ws.Range(model.changing).Value = 0
            results.append(solve(xl, book, model))
    return results
