"""Tests for date search functionality."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from gflightscli.lib.errors import NotFoundError
from gflightscli.lib.fli_bridge import search_dates, _normalize_date_price


def _make_date_price(date_str: str, price: float, return_date: str | None = None):
    dp = MagicMock()
    dp.price = price
    if return_date:
        dp.date = (datetime.strptime(date_str, "%Y-%m-%d"),
                    datetime.strptime(return_date, "%Y-%m-%d"))
    else:
        dp.date = (datetime.strptime(date_str, "%Y-%m-%d"),)
    return dp


def test_normalize_one_way_date():
    dp = _make_date_price("2026-04-01", 250.0)
    result = _normalize_date_price(dp)
    assert result["date"] == "2026-04-01"
    assert result["price"] == 250.0
    assert "return_date" not in result


def test_normalize_round_trip_date():
    dp = _make_date_price("2026-04-01", 450.0, "2026-04-10")
    result = _normalize_date_price(dp)
    assert result["departure_date"] == "2026-04-01"
    assert result["return_date"] == "2026-04-10"
    assert result["price"] == 450.0


@patch("gflightscli.lib.fli_bridge.SearchDates")
def test_search_dates_no_results(mock_cls):
    mock_instance = MagicMock()
    mock_instance.search.return_value = None
    mock_cls.return_value = mock_instance

    with pytest.raises(NotFoundError, match="No date prices"):
        search_dates("SEA", "JFK", "2026-04-01", "2026-06-01")


@patch("gflightscli.lib.fli_bridge.SearchDates")
def test_search_dates_returns_sorted(mock_cls):
    mock_instance = MagicMock()
    mock_instance.search.return_value = [
        _make_date_price("2026-04-05", 300.0),
        _make_date_price("2026-04-10", 200.0),
        _make_date_price("2026-04-15", 250.0),
    ]
    mock_cls.return_value = mock_instance

    results = search_dates("SEA", "JFK", "2026-04-01", "2026-05-01")
    assert len(results) == 3
    prices = [r["price"] for r in results]
    assert 200.0 in prices
