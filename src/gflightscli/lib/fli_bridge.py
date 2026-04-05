"""Bridge between CLI string inputs and fli library types.

This is the ONLY module that imports from fli. All other code uses plain dicts.
"""

from __future__ import annotations

from datetime import datetime

from fli.core.builders import build_date_search_segments, build_flight_segments
from fli.core.parsers import (
    Airport,
    MaxStops,
    SeatType,
    SortBy,
    parse_airlines,
    parse_cabin_class,
    parse_max_stops,
    parse_sort_by,
    resolve_airport,
    ParseError,
)
from fli.models import (
    DateSearchFilters,
    FlightSearchFilters,
    PassengerInfo,
    TimeRestrictions,
    TripType,
)
from fli.models.google_flights.base import FlightResult, FlightLeg
from fli.search import SearchDates, SearchFlights
from fli.search.dates import DatePrice

from gflightscli.lib.errors import APIError, NotFoundError, ValidationError


# ── Enum resolution ──────────────────────────────────────────────────────────

def resolve_airport_code(code: str) -> Airport:
    """Resolve an IATA code string to an Airport enum member."""
    try:
        return resolve_airport(code.upper())
    except (ParseError, KeyError, AttributeError) as e:
        raise ValidationError(f"Unknown airport code: {code}") from e


def resolve_seat_type(name: str) -> SeatType:
    try:
        return parse_cabin_class(name.upper())
    except (ParseError, KeyError, ValueError) as e:
        raise ValidationError(f"Unknown cabin class: {name}") from e


def resolve_max_stops(name: str) -> MaxStops:
    try:
        return parse_max_stops(name.upper())
    except (ParseError, KeyError, ValueError) as e:
        raise ValidationError(f"Unknown stops value: {name}") from e


def resolve_sort_by(name: str) -> SortBy:
    try:
        return parse_sort_by(name.upper())
    except (ParseError, KeyError, ValueError) as e:
        raise ValidationError(f"Unknown sort value: {name}") from e


def resolve_airline_list(codes: list[str] | None):
    if not codes:
        return None
    try:
        return parse_airlines(codes)
    except (ParseError, KeyError, ValueError) as e:
        raise ValidationError(f"Unknown airline code(s): {codes}") from e


# ── Search wrappers ──────────────────────────────────────────────────────────

def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str | None = None,
    cabin_class: str = "ECONOMY",
    max_stops: str = "ANY",
    sort_by: str = "CHEAPEST",
    airlines: list[str] | None = None,
    adults: int = 1,
    top_n: int = 10,
) -> list[dict]:
    """Search flights and return normalized dicts."""
    origin_ap = resolve_airport_code(origin)
    dest_ap = resolve_airport_code(destination)
    seat = resolve_seat_type(cabin_class)
    stops = resolve_max_stops(max_stops)
    sort = resolve_sort_by(sort_by)
    airline_list = resolve_airline_list(airlines)

    segments, trip_type = build_flight_segments(
        origin=origin_ap,
        destination=dest_ap,
        departure_date=departure_date,
        return_date=return_date,
    )

    filters = FlightSearchFilters(
        trip_type=trip_type,
        passenger_info=PassengerInfo(adults=adults),
        flight_segments=segments,
        stops=stops,
        seat_type=seat,
        airlines=airline_list,
        sort_by=sort,
    )

    try:
        results = SearchFlights().search(filters, top_n=top_n)
    except Exception as e:
        raise APIError(f"Google Flights API error: {e}") from e

    if not results:
        raise NotFoundError("No flights found for this route and date.")

    return [_normalize_flight_result(r) for r in results]


def search_dates(
    origin: str,
    destination: str,
    from_date: str,
    to_date: str,
    duration: int | None = None,
    is_round_trip: bool = False,
    cabin_class: str = "ECONOMY",
    max_stops: str = "ANY",
    airlines: list[str] | None = None,
    adults: int = 1,
) -> list[dict]:
    """Search date prices and return normalized dicts."""
    origin_ap = resolve_airport_code(origin)
    dest_ap = resolve_airport_code(destination)
    seat = resolve_seat_type(cabin_class)
    stops = resolve_max_stops(max_stops)
    airline_list = resolve_airline_list(airlines)

    segments, trip_type = build_date_search_segments(
        origin=origin_ap,
        destination=dest_ap,
        start_date=from_date,
        trip_duration=duration,
        is_round_trip=is_round_trip,
    )

    filters = DateSearchFilters(
        trip_type=trip_type,
        passenger_info=PassengerInfo(adults=adults),
        flight_segments=segments,
        stops=stops,
        seat_type=seat,
        airlines=airline_list,
        from_date=from_date,
        to_date=to_date,
        duration=duration,
    )

    try:
        results = SearchDates().search(filters)
    except Exception as e:
        raise APIError(f"Google Flights API error: {e}") from e

    if not results:
        raise NotFoundError("No date prices found for this route.")

    return [_normalize_date_price(dp) for dp in results]


def lookup_airports(query: str) -> list[dict]:
    """Search Airport enum for matches on code or name."""
    query_upper = query.upper()
    query_lower = query.lower()
    matches = []
    for ap in Airport:
        if query_upper in ap.name or query_lower in ap.value.lower():
            matches.append({"code": ap.name, "name": ap.value})
    if not matches:
        raise NotFoundError(f"No airports matching '{query}'.")
    return matches


# ── Normalization ────────────────────────────────────────────────────────────

def _normalize_flight_result(result) -> dict:
    """Convert a FlightResult (or tuple of FlightResults for round-trip) to a dict."""
    if isinstance(result, tuple):
        outbound, returning = result
        # Google Flights returns the total RT fare on each leg, not per-leg prices.
        # The return leg's price after outbound selection is the definitive RT total.
        return {
            "outbound": _single_flight_to_dict(outbound),
            "return": _single_flight_to_dict(returning),
            "total_price": returning.price,
            "total_duration_minutes": outbound.duration + returning.duration,
        }
    return _single_flight_to_dict(result)


def _single_flight_to_dict(fr: FlightResult) -> dict:
    return {
        "price": fr.price,
        "duration_minutes": fr.duration,
        "stops": fr.stops,
        "legs": [_leg_to_dict(leg) for leg in fr.legs],
    }


def _leg_to_dict(leg: FlightLeg) -> dict:
    return {
        "airline": leg.airline.name if hasattr(leg.airline, "name") else str(leg.airline),
        "flight_number": leg.flight_number,
        "departure_airport": leg.departure_airport.name,
        "arrival_airport": leg.arrival_airport.name,
        "departure_time": leg.departure_datetime.isoformat(),
        "arrival_time": leg.arrival_datetime.isoformat(),
        "duration_minutes": leg.duration,
    }


def _normalize_date_price(dp: DatePrice) -> dict:
    dates = dp.date
    if len(dates) == 2:
        return {
            "departure_date": dates[0].strftime("%Y-%m-%d"),
            "return_date": dates[1].strftime("%Y-%m-%d"),
            "price": dp.price,
        }
    return {
        "date": dates[0].strftime("%Y-%m-%d"),
        "price": dp.price,
    }
