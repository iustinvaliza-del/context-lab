# Data case: Rambla Coffee (invented)

**The case.** Rambla Coffee, a kiosk on La Rambla, tried six prices for a cup over twelve weeks and wrote down the cups sold. The file `rambla.xlsx` has two columns, price (EUR) and cups per week:

| Price | 2.0 | 2.2 | 2.4 | 2.6 | 2.8 | 3.0 | 2.0 | 2.2 | 2.4 | 2.6 | 2.8 | 3.0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Cups | 1210 | 1150 | 1105 | 1040 | 980 | 905 | 1190 | 1160 | 1090 | 1050 | 965 | 920 |

**Prep questions.** 1. How do sales respond to price? 2. How many cups at EUR 2.50? 3. Which price brings in the most revenue?

## Step a: Python first

```python
import numpy as np
price = np.array([2.0, 2.2, 2.4, 2.6, 2.8, 3.0] * 2)
cups = np.array([1210, 1150, 1105, 1040, 980, 905, 1190, 1160, 1090, 1050, 965, 920])
slope, intercept = np.polyfit(price, cups, 1)       # -291.07, 1791.43
r2 = 1 - ((cups - (intercept + slope * price))**2).sum() / ((cups - cups.mean())**2).sum()   # 0.990
at_250 = intercept + slope * 2.50                   # 1,063.75 cups
best_price = -intercept / (2 * slope)               # 3.08: revenue p x (a + b p) peaks at -a / 2b
```

- Each extra 10 cents loses about 29 cups a week, and price explains 99% of the variation in sales.
- At EUR 2.50 the line predicts 1,064 cups.
- Revenue peaks at about EUR 3.08, just above the highest price tried (EUR 3.00). Say so in the notes: the line is a fit to prices between 2.00 and 3.00, and outside that range it is a guess. The data supports "at least 3.00", not "3.08".

## Steps b to d

- The notes answer the three questions with these numbers marked "workbook check: pending", and add what the data cannot tell: weather, tourists, and whether week 7 repeated week 1 on purpose.
- The workbook puts the twelve rows on an exhibit sheet, computes the slope and intercept with Excel's `SLOPE` and `INTERCEPT` functions, and adds Checks rows for the slope (-291.07), the intercept (1,791.43) and the cups at 2.50 (1,063.75).
- `check_workbook.py` prints "All checks OK"; the notes then say "workbook check: passed".
