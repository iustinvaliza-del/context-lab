# Quantitative case: Lumen Studio (invented)

**The case.** Lumen Studio can sell its new game to a publisher for a guaranteed EUR 2.0M, or launch it alone. Launching alone, the studio expects a hit with probability 40% (profit EUR 8.0M) and a flop with probability 60% (loss EUR 1.0M). A market test would tell, before deciding, whether the game will be a hit.

**Prep questions.** 1. Sell or launch, on expected value? 2. How much is the market test worth at most? 3. What else should the founders weigh?

## Step a: Python first

```python
p_hit, hit, flop, deal = 0.40, 8.0, -1.0, 2.0
emv_launch = p_hit * hit + (1 - p_hit) * flop          # 2.6
best_now = max(emv_launch, deal)                       # 2.6: launch
with_info = p_hit * max(hit, deal) + (1 - p_hit) * max(flop, deal)   # 4.4
evpi = with_info - best_now                            # 1.8
```

Launch has the higher expected value (EUR 2.6M against 2.0M). Perfect information is worth at most EUR 1.8M: a test that costs more is not worth running, whatever it shows.

## Step b: the notes

Organised by the three questions, with "workbook check: pending" next to 2.6, 4.4 and 1.8. Question 3 is discussion: the founders' appetite for risk (a 60% chance of losing EUR 1M), and what the deal gives up.

## Step c: the workbook

`_build/build_LUMEN.py` in the session folder:

```python
# /// script
# dependencies = ["openpyxl"]
# ///
import sys
from pathlib import Path
root = next(p for p in Path(__file__).resolve().parents if (p / "pipeline" / "workbook.py").exists())
sys.path.insert(0, str(root / "pipeline"))  # the project's pipeline/ folder, however deep this file is
from workbook import CaseWorkbook, FMT_DEC

wb = CaseWorkbook(case="Lumen Studio", course="Decision Analysis", session=3,
                  questions=["Sell or launch, on expected value?", "How much is the market test worth at most?"])
p = wb.add_input("Probability of a hit", 0.40, source="Case p.1")
hit = wb.add_input("Profit if hit (EUR M)", 8.0, source="Case p.1", fmt=FMT_DEC)
flop = wb.add_input("Profit if flop (EUR M)", -1.0, source="Case p.1", fmt=FMT_DEC)
deal = wb.add_input("Publisher deal (EUR M)", 2.0, source="Case p.1", fmt=FMT_DEC)
ws = wb.add_exhibit("Decision tree", caption="Expected value of each choice", headers=["Step", "Formula", "EUR M"])
r1 = CaseWorkbook.row(ws, "Expected value of launching", "p x hit + (1-p) x flop", f"={p}*{hit}+(1-{p})*{flop}", fmt=FMT_DEC)
r2 = CaseWorkbook.row(ws, "Best choice now", "max(launch, deal)", f"=MAX(D{r1},{deal})", result=True, fmt=FMT_DEC)
r3 = CaseWorkbook.row(ws, "Value with perfect information", "p x max(hit, deal) + (1-p) x max(flop, deal)",
                      f"={p}*MAX({hit},{deal})+(1-{p})*MAX({flop},{deal})", fmt=FMT_DEC)
r4 = CaseWorkbook.row(ws, "Most the test is worth", "with information - best now", f"=D{r3}-D{r2}", result=True, fmt=FMT_DEC)
wb.add_check("EMV of launching = Python", 2.6, f"='1 Decision tree'!D{r1}", fmt=FMT_DEC)
wb.add_check("Value of the test = Python", 1.8, f"='1 Decision tree'!D{r4}", fmt=FMT_DEC)
wb.add_assumption("Profits are as stated, no discounting", "The case gives one-period profits", "")
wb.save(str(Path(__file__).resolve().parents[1] / "LUMEN_WORKBOOK.xlsx"))
```

## Step d: the check

`uv run pipeline/check_workbook.py "<session folder>/LUMEN_WORKBOOK.xlsx"` prints both rows as OK and "All checks OK". Only then do the notes say "workbook check: passed".

`check_workbook.py` allows 0.5 for large numbers, two-decimal rounding from 1 up, and 0.0005 for rates, so 2.6 cannot pass as 2.2. The Checks sheet's own OK/FAIL column inside Excel allows 0.5 everywhere, which is why the Python check is the one that counts.
