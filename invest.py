# --- CONFIG (edit these) ---
BUDGET = 1000  # dollars
TICKERS = ["VOO", "QQQ", "VTI", "SCHD", "BND", "GLD"]
# ---------------------------

import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta


def calculate_return(price_today: float, price_1yr_ago: float) -> float:
    """Return the fractional 1-year return (e.g. 0.20 for +20%)."""
    return (price_today - price_1yr_ago) / price_1yr_ago


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


def generate_notes(
    ticker: str,
    return_pct: float | None,
    _allocation: float,
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
        except (ValueError, KeyError, IndexError, AttributeError):
            results[ticker] = {"return_pct": None, "status": "unavailable"}

    return results


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


def main():
    pass


if __name__ == "__main__":
    main()
