# Optimisation case: Pyrenees Furniture (invented)

**The case.** A workshop makes tables (profit EUR 120 each) and chairs (EUR 50 each). A table needs 4 hours of carpentry and 2 of finishing; a chair needs 1 and 2. Each week there are 100 hours of carpentry and 80 of finishing.

**Prep questions.** 1. How many tables and chairs a week? 2. What is one more hour of carpentry worth, and one more hour of finishing?

## Step a: Python first

```python
from scipy.optimize import linprog
res = linprog(c=[-120, -50],                       # maximise, so the profits are negative
              A_ub=[[4, 1], [2, 2]], b_ub=[100, 80], method="highs")
plan = res.x                                       # [20, 20]
profit = -res.fun                                  # 3,400
shadow = -res.ineqlin.marginals                    # [23.33, 13.33] per extra hour
```

Make 20 tables and 20 chairs for EUR 3,400 a week. Both limits are used up. One more hour of carpentry is worth EUR 23.33, one more of finishing EUR 13.33, as long as the plan's shape does not change.

## Step c: the workbook

- Inputs: the two profits, the four hours per unit, the two limits.
- Model sheet: two decision cells holding the Python plan (20 and 20), a SUMPRODUCT row for profit, and a SUMPRODUCT row for each limit's hours used, next to the limit.
- Checks: profit = 3,400; carpentry used = 100; finishing used = 80.
- `check_workbook.py` proves the layout gives the same answer as the Python solve.
- On Windows with Excel, `solver_runner.py` can also set Solver up in the file (objective, decision cells, the two limits), solve it and keep the Sensitivity Report, so the shadow prices are in Excel too. On a Mac, the notes say Solver setup is left to you.

The shadow prices are Python's; quote them from the Python solve, or from the Sensitivity Report when Solver ran on Windows.
