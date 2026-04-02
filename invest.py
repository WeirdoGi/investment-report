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


def main():
    pass


if __name__ == "__main__":
    main()
