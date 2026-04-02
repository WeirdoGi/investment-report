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


def main():
    pass


if __name__ == "__main__":
    main()
