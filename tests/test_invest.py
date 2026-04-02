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
