"""Tests for flight search via fli_bridge."""

from __future__ import annotations

from unittest.mock import MagicMock, patch
from datetime import datetime

import pytest

from gflightscli.lib.errors import NotFoundError, ValidationError
from gflightscli.lib.fli_bridge import (
    lookup_airports,
    resolve_airport_code,
    resolve_max_stops,
    resolve_seat_type,
    resolve_sort_by,
    search_flights,
    _normalize_flight_result,
    _leg_to_dict,
)


def test_resolve_airport_valid():
    ap = resolve_airport_code("JFK")
    assert ap.name == "JFK"


def test_resolve_airport_lowercase():
    ap = resolve_airport_code("jfk")
    assert ap.name == "JFK"


def test_resolve_airport_invalid():
    with pytest.raises(ValidationError, match="Unknown airport"):
        resolve_airport_code("ZZZZZZ")


def test_resolve_seat_type_economy():
    st = resolve_seat_type("ECONOMY")
    assert st.value == 1


def test_resolve_seat_type_business():
    st = resolve_seat_type("business")
    assert st.value == 3


def test_resolve_seat_type_invalid():
    with pytest.raises(ValidationError, match="Unknown cabin"):
        resolve_seat_type("SUPER_DELUXE")


def test_resolve_max_stops_any():
    ms = resolve_max_stops("ANY")
    assert ms.value == 0


def test_resolve_sort_cheapest():
    sb = resolve_sort_by("CHEAPEST")
    assert sb.value == 2


def test_lookup_airports_by_code():
    results = lookup_airports("JFK")
    assert any(r["code"] == "JFK" for r in results)


def test_lookup_airports_by_name():
    results = lookup_airports("seattle")
    assert len(results) > 0


def test_lookup_airports_not_found():
    with pytest.raises(NotFoundError):
        lookup_airports("xyzzyplugh")


def test_normalize_single_flight():
    """Test normalization of a mock FlightResult."""
    leg = MagicMock()
    leg.airline.name = "AA"
    leg.flight_number = "AA100"
    leg.departure_airport.name = "SEA"
    leg.arrival_airport.name = "JFK"
    leg.departure_datetime = datetime(2026, 4, 1, 8, 0)
    leg.arrival_datetime = datetime(2026, 4, 1, 16, 30)
    leg.duration = 330

    flight = MagicMock()
    flight.price = 350.0
    flight.duration = 330
    flight.stops = 0
    flight.legs = [leg]

    result = _normalize_flight_result(flight)
    assert result["price"] == 350.0
    assert result["stops"] == 0
    assert len(result["legs"]) == 1
    assert result["legs"][0]["airline"] == "AA"


def test_normalize_round_trip():
    """Test normalization of a round-trip tuple."""
    def make_flight(price, dur):
        leg = MagicMock()
        leg.airline.name = "UA"
        leg.flight_number = "UA200"
        leg.departure_airport.name = "SEA"
        leg.arrival_airport.name = "EZE"
        leg.departure_datetime = datetime(2026, 4, 1, 10, 0)
        leg.arrival_datetime = datetime(2026, 4, 2, 6, 0)
        leg.duration = dur
        f = MagicMock()
        f.price = price
        f.duration = dur
        f.stops = 1
        f.legs = [leg]
        return f

    out = make_flight(400, 600)
    ret = make_flight(380, 580)
    result = _normalize_flight_result((out, ret))
    assert result["total_price"] == 780
    assert result["total_duration_minutes"] == 1180
    assert "outbound" in result
    assert "return" in result


@patch("gflightscli.lib.fli_bridge.SearchFlights")
def test_search_flights_no_results(mock_search_cls):
    mock_instance = MagicMock()
    mock_instance.search.return_value = None
    mock_search_cls.return_value = mock_instance

    with pytest.raises(NotFoundError, match="No flights found"):
        search_flights("SEA", "JFK", "2026-04-01")
