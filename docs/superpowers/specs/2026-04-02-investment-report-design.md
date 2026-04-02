# Investment Report Generator — Design Spec

**Date:** 2026-04-02
**Status:** Approved

---

## Overview

A Python script that fetches live financial data, ranks a hardcoded list of investment candidates by 1-year return, allocates a hardcoded budget proportionally across positive-return candidates, and generates a self-contained HTML report with an interactive pie chart and ranked table.

---

## Architecture

A single Python script (`invest.py`) with a config block at the top. When run, it:

1. Reads the hardcoded budget and ticker list from the config block
2. Fetches 1-year historical price data for each ticker via `yfinance`
3. Calculates 1-year return % for each ticker
4. Allocates the budget proportionally across tickers with positive returns
5. Generates `report.html` with an embedded Plotly chart and ranked table

No web server required. The HTML report is fully self-contained and opens in any browser.

---

## Config Block

At the top of `invest.py`:

```python
BUDGET = 1000  # dollars — change this to your budget
TICKERS = ["VOO", "QQQ", "VTI", "SCHD", "BND", "GLD"]  # candidates to evaluate
```

Both values are the only things a user needs to modify.

---

## Data & Allocation Logic

**Data source:** `yfinance` — no API key required, free, pulls from Yahoo Finance.

**Return calculation:**
```
return % = (price_today - price_1yr_ago) / price_1yr_ago
```
Uses the closing price from exactly 365 days ago and today's most recent closing price.

**Allocation logic:**
- Only tickers with positive 1-year returns are allocated budget
- Budget is split proportionally: `allocation = (ticker_return / sum_of_positive_returns) * BUDGET`
- Tickers with zero or negative returns receive $0 and are excluded from the pie chart

---

## HTML Report Structure

Three sections, generated as a single `report.html` file (overwritten on each run):

1. **Summary bar** — budget total, number of candidates evaluated, date generated
2. **Pie chart** — interactive Plotly chart showing dollar allocation per ticker; hover reveals exact amounts
3. **Ranked table** — all candidates sorted by 1-year return %, columns:
   - Ticker
   - 1-Year Return %
   - Allocated $
   - Notes (e.g., "Highest return at 24.3%" or "Excluded: negative return (-3.1%)")

Negative-return tickers appear at the bottom of the table in gray with $0 and an explanation.

Plotly chart is embedded inline — no CDN or internet required to view the report after generation.

---

## Error Handling

Only at the API boundary:

| Scenario | Behavior |
|---|---|
| Single ticker fails to fetch | Skip it; mark as "data unavailable" in the report table |
| All tickers fail to fetch | Print a clear error message and exit without generating a report |
| All tickers have negative returns | Generate the report; note that no allocation was made and explain why |

---

## Project Structure

```
invest.py          # the script
report.html        # generated output (overwritten each run)
requirements.txt   # yfinance, plotly
```

---

## Dependencies

- `yfinance` — historical price data
- `plotly` — interactive pie chart, embedded inline in HTML

---

## Success Criteria

- Running `python invest.py` produces a `report.html` in the same directory
- The report opens in any browser without an internet connection
- The pie chart is interactive (hover shows $ amounts)
- The table correctly excludes negative-return tickers from allocation
- A single-ticker fetch failure does not crash the script
