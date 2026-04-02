# Investment Report Generator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python script that fetches live stock/ETF data, allocates a hardcoded budget proportionally by 1-year return, and outputs a self-contained HTML report with an interactive pie chart and ranked table.

**Architecture:** A single `invest.py` script with pure functions for calculation logic, a `yfinance` data-fetching layer with per-ticker error handling, and a Plotly-based HTML generator. All logic is unit-tested with mocked external calls; running `python invest.py` writes `report.html` to the same directory.

**Tech Stack:** Python 3.8+, `yfinance`, `plotly`

---

## File Structure

| File | Responsibility |
|---|---|
| `invest.py` | Config block, all functions, `main()` entry point |
| `requirements.txt` | `yfinance` and `plotly` dependencies |
| `tests/test_invest.py` | All unit tests (mocked yfinance) |
| `report.html` | Generated output — not committed, overwritten each run |

---

## Task 1: Project Setup

**Files:**
- Create: `requirements.txt`
- Create: `tests/__init__.py`
- Create: `tests/test_invest.py`
- Create: `invest.py` (skeleton only)

- [ ] **Step 1: Create `requirements.txt`**

```
yfinance==0.2.58
plotly==5.22.0
```

- [ ] **Step 2: Install dependencies**

Run:
```bash
pip install -r requirements.txt
```
Expected: both packages install without errors.

- [ ] **Step 3: Create skeleton `invest.py`**

```python
# --- CONFIG (edit these) ---
BUDGET = 1000  # dollars
TICKERS = ["VOO", "QQQ", "VTI", "SCHD", "BND", "GLD"]
# ---------------------------

import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta


def main():
    pass


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Create `tests/__init__.py`**

Empty file — just needs to exist:
```python
```

- [ ] **Step 5: Create `tests/test_invest.py` with a smoke test**

```python
import pytest
from invest import calculate_return
```

- [ ] **Step 6: Run the smoke test to verify imports work**

Run:
```bash
pytest tests/test_invest.py -v
```
Expected: FAIL with `ImportError: cannot import name 'calculate_return' from 'invest'` — that's correct, function doesn't exist yet.

- [ ] **Step 7: Commit**

```bash
git init  # only if not already a git repo
git add invest.py requirements.txt tests/__init__.py tests/test_invest.py
git commit -m "chore: project skeleton and dependencies"
```

---

## Task 2: Return Calculation

**Files:**
- Modify: `invest.py` — add `calculate_return()`
- Modify: `tests/test_invest.py` — add tests

- [ ] **Step 1: Write failing tests**

Replace `tests/test_invest.py` with:

```python
import pytest
from invest import calculate_return


def test_positive_return():
    # Stock went from $100 to $120 — 20% return
    assert calculate_return(120.0, 100.0) == pytest.approx(0.20)


def test_negative_return():
    # Stock went from $100 to $80 — -20% return
    assert calculate_return(80.0, 100.0) == pytest.approx(-0.20)


def test_zero_return():
    # Price unchanged
    assert calculate_return(100.0, 100.0) == pytest.approx(0.0)


def test_large_gain():
    assert calculate_return(250.0, 100.0) == pytest.approx(1.50)
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
pytest tests/test_invest.py -v
```
Expected: 4 failures with `ImportError: cannot import name 'calculate_return'`

- [ ] **Step 3: Implement `calculate_return` in `invest.py`**

Add after the imports block:

```python
def calculate_return(price_today: float, price_1yr_ago: float) -> float:
    """Return the fractional 1-year return (e.g. 0.20 for +20%)."""
    return (price_today - price_1yr_ago) / price_1yr_ago
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
pytest tests/test_invest.py -v
```
Expected: 4 PASS

- [ ] **Step 5: Commit**

```bash
git add invest.py tests/test_invest.py
git commit -m "feat: add calculate_return function"
```

---

## Task 3: Budget Allocation Logic

**Files:**
- Modify: `invest.py` — add `allocate_budget()`
- Modify: `tests/test_invest.py` — add tests

- [ ] **Step 1: Write failing tests**

Append to `tests/test_invest.py`:

```python
from invest import allocate_budget


def test_allocation_proportional():
    # VOO returned 30%, QQQ returned 10% — VOO should get 75%, QQQ 25%
    result = allocate_budget(1000.0, {"VOO": 0.30, "QQQ": 0.10})
    assert result["VOO"] == pytest.approx(750.0)
    assert result["QQQ"] == pytest.approx(250.0)


def test_allocation_excludes_negative_returns():
    result = allocate_budget(1000.0, {"VOO": 0.20, "BND": -0.05})
    assert result["VOO"] == pytest.approx(1000.0)
    assert result["BND"] == pytest.approx(0.0)


def test_allocation_excludes_zero_returns():
    result = allocate_budget(1000.0, {"VOO": 0.20, "GLD": 0.0})
    assert result["VOO"] == pytest.approx(1000.0)
    assert result["GLD"] == pytest.approx(0.0)


def test_allocation_all_negative_returns_zero():
    result = allocate_budget(1000.0, {"VOO": -0.10, "BND": -0.05})
    assert result["VOO"] == pytest.approx(0.0)
    assert result["BND"] == pytest.approx(0.0)


def test_allocation_single_winner_gets_full_budget():
    result = allocate_budget(500.0, {"VOO": 0.15})
    assert result["VOO"] == pytest.approx(500.0)
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
pytest tests/test_invest.py -v -k "allocation"
```
Expected: 5 failures with `ImportError: cannot import name 'allocate_budget'`

- [ ] **Step 3: Implement `allocate_budget` in `invest.py`**

Add after `calculate_return`:

```python
def allocate_budget(budget: float, ticker_returns: dict[str, float]) -> dict[str, float]:
    """
    Proportionally allocate budget across tickers with positive returns.
    Returns a dict of ticker -> dollar amount (0.0 for non-positive returns).
    """
    positive = {t: r for t, r in ticker_returns.items() if r > 0}
    total_positive = sum(positive.values())

    result = {t: 0.0 for t in ticker_returns}
    if total_positive > 0:
        for ticker, ret in positive.items():
            result[ticker] = (ret / total_positive) * budget
    return result
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
pytest tests/test_invest.py -v
```
Expected: all tests PASS

- [ ] **Step 5: Commit**

```bash
git add invest.py tests/test_invest.py
git commit -m "feat: add allocate_budget function"
```

---

## Task 4: Notes Generation

**Files:**
- Modify: `invest.py` — add `generate_notes()`
- Modify: `tests/test_invest.py` — add tests

- [ ] **Step 1: Write failing tests**

Append to `tests/test_invest.py`:

```python
from invest import generate_notes


def test_notes_highest_return():
    # VOO has the highest return among the set
    note = generate_notes("VOO", 0.30, 750.0, {"VOO": 0.30, "QQQ": 0.10})
    assert "highest" in note.lower()
    assert "30.0%" in note


def test_notes_positive_not_highest():
    note = generate_notes("QQQ", 0.10, 250.0, {"VOO": 0.30, "QQQ": 0.10})
    assert "10.0%" in note
    assert "highest" not in note.lower()


def test_notes_negative_return():
    note = generate_notes("BND", -0.05, 0.0, {"VOO": 0.20, "BND": -0.05})
    assert "excluded" in note.lower()
    assert "-5.0%" in note


def test_notes_zero_return():
    note = generate_notes("GLD", 0.0, 0.0, {"VOO": 0.20, "GLD": 0.0})
    assert "excluded" in note.lower()


def test_notes_data_unavailable():
    note = generate_notes("XYZ", None, 0.0, {"VOO": 0.20, "XYZ": None})
    assert "unavailable" in note.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
pytest tests/test_invest.py -v -k "notes"
```
Expected: 5 failures with `ImportError: cannot import name 'generate_notes'`

- [ ] **Step 3: Implement `generate_notes` in `invest.py`**

Add after `allocate_budget`:

```python
def generate_notes(
    ticker: str,
    return_pct: float | None,
    allocation: float,
    all_returns: dict[str, float | None],
) -> str:
    """Generate a human-readable explanation for a ticker's placement in the report."""
    if return_pct is None:
        return "Data unavailable — skipped"
    pct_str = f"{return_pct * 100:.1f}%"
    if return_pct <= 0:
        return f"Excluded: {'negative' if return_pct < 0 else 'zero'} return ({pct_str})"
    valid_returns = [r for r in all_returns.values() if r is not None and r > 0]
    if valid_returns and return_pct == max(valid_returns):
        return f"Highest 1-year return in candidate list at {pct_str}"
    return f"Positive 1-year return of {pct_str}"
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
pytest tests/test_invest.py -v
```
Expected: all tests PASS

- [ ] **Step 5: Commit**

```bash
git add invest.py tests/test_invest.py
git commit -m "feat: add generate_notes function"
```

---

## Task 5: Data Fetching (with Error Handling)

**Files:**
- Modify: `invest.py` — add `fetch_ticker_data()`
- Modify: `tests/test_invest.py` — add tests

- [ ] **Step 1: Write failing tests**

Append to `tests/test_invest.py`:

```python
from unittest.mock import patch, MagicMock
import pandas as pd
from invest import fetch_ticker_data


def _make_mock_ticker(price_today, price_1yr_ago):
    """Helper: returns a mock yfinance Ticker with history() returning two prices."""
    mock_ticker = MagicMock()
    dates = pd.date_range(end=pd.Timestamp.today(), periods=2, freq="365D")
    mock_ticker.history.return_value = pd.DataFrame(
        {"Close": [price_1yr_ago, price_today]}, index=dates
    )
    return mock_ticker


def test_fetch_returns_correct_return_pct():
    with patch("invest.yf.Ticker") as mock_yf:
        mock_yf.return_value = _make_mock_ticker(120.0, 100.0)
        result = fetch_ticker_data(["VOO"])
    assert result["VOO"]["return_pct"] == pytest.approx(0.20)
    assert result["VOO"]["status"] == "ok"


def test_fetch_single_ticker_failure_does_not_crash():
    def side_effect(ticker):
        if ticker == "BAD":
            m = MagicMock()
            m.history.return_value = pd.DataFrame()  # empty — simulates fetch failure
            return m
        return _make_mock_ticker(120.0, 100.0)

    with patch("invest.yf.Ticker", side_effect=side_effect):
        result = fetch_ticker_data(["VOO", "BAD"])

    assert result["VOO"]["status"] == "ok"
    assert result["BAD"]["status"] == "unavailable"
    assert result["BAD"]["return_pct"] is None


def test_fetch_all_tickers_fail_returns_all_unavailable():
    with patch("invest.yf.Ticker") as mock_yf:
        m = MagicMock()
        m.history.return_value = pd.DataFrame()
        mock_yf.return_value = m
        result = fetch_ticker_data(["VOO", "QQQ"])

    assert result["VOO"]["status"] == "unavailable"
    assert result["QQQ"]["status"] == "unavailable"
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
pytest tests/test_invest.py -v -k "fetch"
```
Expected: 3 failures with `ImportError: cannot import name 'fetch_ticker_data'`

- [ ] **Step 3: Implement `fetch_ticker_data` in `invest.py`**

Add after `generate_notes`:

```python
def fetch_ticker_data(tickers: list[str]) -> dict[str, dict]:
    """
    Fetch 1-year price data for each ticker via yfinance.
    Returns {ticker: {"return_pct": float|None, "status": "ok"|"unavailable"}}
    """
    results = {}
    end = datetime.today()
    start = end - timedelta(days=370)  # slightly more than 365 to ensure coverage

    for ticker in tickers:
        try:
            hist = yf.Ticker(ticker).history(start=start, end=end)
            if hist.empty or len(hist) < 2:
                raise ValueError("Insufficient data")
            price_1yr_ago = hist["Close"].iloc[0]
            price_today = hist["Close"].iloc[-1]
            results[ticker] = {
                "return_pct": calculate_return(price_today, price_1yr_ago),
                "status": "ok",
            }
        except Exception:
            results[ticker] = {"return_pct": None, "status": "unavailable"}

    return results
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
pytest tests/test_invest.py -v
```
Expected: all tests PASS

- [ ] **Step 5: Commit**

```bash
git add invest.py tests/test_invest.py
git commit -m "feat: add fetch_ticker_data with per-ticker error handling"
```

---

## Task 6: HTML Report Generation

**Files:**
- Modify: `invest.py` — add `generate_html()`
- Modify: `tests/test_invest.py` — add tests

- [ ] **Step 1: Write failing tests**

Append to `tests/test_invest.py`:

```python
from invest import generate_html


SAMPLE_RESULTS = [
    {"ticker": "VOO", "return_pct": 0.24, "allocation": 750.0, "notes": "Highest 1-year return in candidate list at 24.0%", "status": "ok"},
    {"ticker": "QQQ", "return_pct": 0.08, "allocation": 250.0, "notes": "Positive 1-year return of 8.0%", "status": "ok"},
    {"ticker": "BND", "return_pct": -0.03, "allocation": 0.0,  "notes": "Excluded: negative return (-3.0%)", "status": "ok"},
    {"ticker": "XYZ", "return_pct": None,  "allocation": 0.0,  "notes": "Data unavailable — skipped", "status": "unavailable"},
]


def test_html_contains_summary_bar():
    html = generate_html(1000.0, SAMPLE_RESULTS, "2026-04-02")
    assert "$1,000.00" in html
    assert "2026-04-02" in html
    assert "4" in html  # number of candidates evaluated


def test_html_contains_ticker_names():
    html = generate_html(1000.0, SAMPLE_RESULTS, "2026-04-02")
    for ticker in ["VOO", "QQQ", "BND", "XYZ"]:
        assert ticker in html


def test_html_contains_plotly_script():
    html = generate_html(1000.0, SAMPLE_RESULTS, "2026-04-02")
    assert "plotly" in html.lower()


def test_html_is_self_contained():
    # Must not reference any external CDN URLs
    html = generate_html(1000.0, SAMPLE_RESULTS, "2026-04-02")
    assert "cdn.plot.ly" not in html
    assert "cdn.jsdelivr" not in html


def test_html_excluded_tickers_appear_in_table():
    html = generate_html(1000.0, SAMPLE_RESULTS, "2026-04-02")
    assert "Excluded" in html
    assert "unavailable" in html.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
pytest tests/test_invest.py -v -k "html"
```
Expected: 5 failures with `ImportError: cannot import name 'generate_html'`

- [ ] **Step 3: Implement `generate_html` in `invest.py`**

Add after `fetch_ticker_data`:

```python
def generate_html(budget: float, results: list[dict], generated_date: str) -> str:
    """
    Build a self-contained HTML report string with:
    - Summary bar (budget, candidate count, date)
    - Plotly pie chart of allocations (positive-return tickers only)
    - Ranked table of all candidates
    """
    # --- Pie chart (only allocated tickers) ---
    pie_data = [(r["ticker"], r["allocation"]) for r in results if r["allocation"] > 0]
    if pie_data:
        labels, values = zip(*pie_data)
        fig = go.Figure(go.Pie(
            labels=labels,
            values=values,
            hovertemplate="%{label}: $%{value:.2f}<extra></extra>",
            textinfo="label+percent",
        ))
        fig.update_layout(title="Budget Allocation by 1-Year Return", margin=dict(t=50, b=0))
        chart_html = fig.to_html(full_html=False, include_plotlyjs=True)
    else:
        chart_html = "<p><em>No positive-return tickers found — no allocation made.</em></p>"

    # --- Table rows ---
    def row_style(r):
        if r["return_pct"] is None or r["return_pct"] <= 0:
            return ' style="color: #999;"'
        return ""

    def fmt_return(r):
        if r["return_pct"] is None:
            return "N/A"
        return f"{r['return_pct'] * 100:.1f}%"

    rows = "\n".join(
        f'<tr{row_style(r)}>'
        f'<td><strong>{r["ticker"]}</strong></td>'
        f'<td>{fmt_return(r)}</td>'
        f'<td>${r["allocation"]:.2f}</td>'
        f'<td>{r["notes"]}</td>'
        f'</tr>'
        for r in results
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Investment Report — {generated_date}</title>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 40px auto; padding: 0 20px; }}
    .summary {{ background: #f4f4f4; padding: 16px 24px; border-radius: 8px; margin-bottom: 24px; display: flex; gap: 40px; }}
    .summary span {{ font-size: 0.85em; color: #555; }}
    .summary strong {{ display: block; font-size: 1.2em; color: #222; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 32px; }}
    th {{ text-align: left; border-bottom: 2px solid #ccc; padding: 8px 12px; }}
    td {{ padding: 8px 12px; border-bottom: 1px solid #eee; }}
  </style>
</head>
<body>
  <h1>Investment Report</h1>

  <div class="summary">
    <div><span>Budget</span><strong>${budget:,.2f}</strong></div>
    <div><span>Candidates Evaluated</span><strong>{len(results)}</strong></div>
    <div><span>Generated</span><strong>{generated_date}</strong></div>
  </div>

  {chart_html}

  <table>
    <thead>
      <tr>
        <th>Ticker</th>
        <th>1-Year Return</th>
        <th>Allocated $</th>
        <th>Notes</th>
      </tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>
</body>
</html>"""
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
pytest tests/test_invest.py -v
```
Expected: all tests PASS

- [ ] **Step 5: Commit**

```bash
git add invest.py tests/test_invest.py
git commit -m "feat: add generate_html function with embedded Plotly chart"
```

---

## Task 7: Wire Everything Together in `main()`

**Files:**
- Modify: `invest.py` — implement `main()`

- [ ] **Step 1: Implement `main()` in `invest.py`**

Replace the existing `def main(): pass` with:

```python
def main():
    print(f"Fetching data for {len(TICKERS)} tickers...")
    raw = fetch_ticker_data(TICKERS)

    if all(v["status"] == "unavailable" for v in raw.values()):
        print("ERROR: Could not fetch data for any ticker. Check your internet connection.")
        return

    ticker_returns = {t: v["return_pct"] for t, v in raw.items()}
    allocations = allocate_budget(BUDGET, {t: r for t, r in ticker_returns.items() if r is not None})

    # Build results list, sorted by return descending (None sorts last)
    results = []
    for ticker, data in raw.items():
        allocation = allocations.get(ticker, 0.0)
        notes = generate_notes(ticker, data["return_pct"], allocation, ticker_returns)
        results.append({
            "ticker": ticker,
            "return_pct": data["return_pct"],
            "allocation": allocation,
            "notes": notes,
            "status": data["status"],
        })

    results.sort(key=lambda r: (r["return_pct"] is None, -(r["return_pct"] or 0)))

    generated_date = datetime.today().strftime("%Y-%m-%d")
    html = generate_html(BUDGET, results, generated_date)

    with open("report.html", "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Report written to report.html")
    print(f"Budget: ${BUDGET:,.2f} across {len(TICKERS)} candidates")
    allocated_count = sum(1 for r in results if r["allocation"] > 0)
    print(f"Allocated to {allocated_count} positive-return ticker(s).")
```

- [ ] **Step 2: Run all tests to make sure nothing broke**

Run:
```bash
pytest tests/ -v
```
Expected: all tests PASS

- [ ] **Step 3: Run the script end-to-end**

Run:
```bash
python invest.py
```
Expected output:
```
Fetching data for 6 tickers...
Report written to report.html
Budget: $1,000.00 across 6 candidates
Allocated to N positive-return ticker(s).
```
A `report.html` file appears in the current directory.

- [ ] **Step 4: Open the report in a browser and verify**

Open `report.html` in a browser. Confirm:
- Summary bar shows budget, 6 candidates, today's date
- Pie chart renders and is hoverable
- Table shows all 6 tickers, sorted by return descending
- Negative/zero-return rows appear in gray at the bottom

- [ ] **Step 5: Final commit**

```bash
git add invest.py
git commit -m "feat: wire main() — script is fully functional"
```

---

## Self-Review Checklist

- [x] **Spec coverage:** Config block ✓, yfinance data fetch ✓, return calculation ✓, proportional allocation ✓, positive-only allocation ✓, summary bar ✓, pie chart (inline Plotly) ✓, ranked table ✓, gray excluded rows ✓, single-ticker failure handling ✓, all-tickers-fail handling ✓, all-negative handling ✓
- [x] **No placeholders:** All steps contain complete code
- [x] **Type consistency:** `calculate_return`, `allocate_budget`, `generate_notes`, `fetch_ticker_data`, `generate_html` signatures are consistent across all tasks
