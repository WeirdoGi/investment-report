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


def main():
    pass


if __name__ == "__main__":
    main()
