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
