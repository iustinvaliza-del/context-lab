# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "formulas>=1.2",
#   "openpyxl",
# ]
# ///
"""Recalculate a case workbook in Python and print its Checks sheet.

The workbook built with workbook.py keeps every result as an Excel formula and has a Checks
sheet: one row per key result, comparing the workbook's formula (Actual) with the number the
prep computed in Python (Expected). This script calculates every formula without Excel, so it
works the same on Windows and on a Mac, and prints each row with OK or FAIL.

    uv run pipeline/check_workbook.py "<workbook.xlsx>"

Exit code 0 when every row reads OK, 1 when a row fails, 2 when the file cannot be calculated.
Quote a workbook number only after this prints "All checks OK".
"""
from __future__ import annotations

import os
import sys
import warnings

os.environ.setdefault("TQDM_DISABLE", "1")  # formulas prints a progress bar otherwise

def tolerance(expected: float) -> float:
    """How far Actual may be from Expected and still read OK.

    0.5 for large numbers, the same rule as the Checks sheet's own Status column; rounding to two decimals for numbers
    from 1 up (2.6 cannot pass as 2.2); 0.0005 for rates and shares below 1, so an IRR of 15.2%
    cannot pass as 15.7%.
    """
    e = abs(expected)
    return min(0.5, max(1e-4 * e, 0.005 if e >= 1 else 0.0005))


def number(value):
    """A calculated cell as a float or text; formulas returns arrays and its own empty markers."""
    try:
        import numpy as np
        if isinstance(value, np.ndarray):
            value = value.ravel()[0] if value.size else None
    except ImportError:
        pass
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        text = str(value)
        return None if text in ("", "empty") else text


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__)
        return 2
    path = argv[0]
    warnings.filterwarnings("ignore")
    import formulas
    from openpyxl import load_workbook

    sheet = load_workbook(path, read_only=True)["Checks"]
    rows = []
    for r in range(5, 30):
        name = sheet[f"B{r}"].value
        if name:
            rows.append((r, name))
    if not rows:
        print("No rows on the Checks sheet: add a check for each key result first.")
        return 1

    try:
        model = formulas.ExcelModel().loads(path).finish()
        solution = model.calculate()
    except Exception as e:
        print(f"Could not calculate {path}: {e}")
        return 2

    def cell(ref: str):
        for key, value in solution.items():
            if key.upper().endswith(f"CHECKS'!{ref}") and "]" in key:
                return number(value.value)
        return None

    failed = 0
    width = max(len(n) for _, n in rows)
    print(f"{'Check'.ljust(width)}  {'Expected':>16}  {'Actual':>16}  Status")
    for r, name in rows:
        expected, actual = cell(f"C{r}"), cell(f"D{r}")
        if isinstance(expected, float) and isinstance(actual, float):
            ok = abs(expected - actual) <= tolerance(expected)
            shown = f"{expected:>16,.2f}  {actual:>16,.2f}"
        else:
            ok = expected is not None and expected == actual
            shown = f"{str(expected):>16}  {str(actual):>16}"
        failed += not ok
        print(f"{name.ljust(width)}  {shown}  {'OK' if ok else 'FAIL'}")
    print("All checks OK" if not failed else f"{failed} check(s) FAIL: fix the workbook before quoting its numbers.")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
