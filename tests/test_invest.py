import pytest
from invest import calculate_return, allocate_budget


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
    # Must not load any external scripts via <script src=...> — Plotly is embedded inline.
    # (The plotly bundle itself contains "cdn.plot.ly" as an internal string, so we check
    # for external script tags specifically rather than raw string presence.)
    html = generate_html(1000.0, SAMPLE_RESULTS, "2026-04-02")
    assert 'src="https://cdn.plot.ly' not in html
    assert 'src="https://cdn.jsdelivr' not in html


def test_html_excluded_tickers_appear_in_table():
    html = generate_html(1000.0, SAMPLE_RESULTS, "2026-04-02")
    assert "Excluded" in html
    assert "unavailable" in html.lower()
