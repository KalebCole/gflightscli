"""dates search + cheapest commands."""

from __future__ import annotations

from datetime import datetime

import click

from gflightscli.lib.errors import GFlightsError, handle_error
from gflightscli.lib.fli_bridge import search_dates
from gflightscli.lib.output import emit, get_ctx_opts


DAY_NAMES = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


@click.group()
def dates():
    """Search for cheapest travel dates."""
    pass


@dates.command()
@click.argument("origin")
@click.argument("destination")
@click.option("--from", "from_date", required=True, help="Start date (YYYY-MM-DD)")
@click.option("--to", "to_date", required=True, help="End date (YYYY-MM-DD)")
@click.option("--duration", "-d", default=None, type=int, help="Trip duration in days")
@click.option("--round-trip", "-R", is_flag=True, help="Round-trip search")
@click.option("--class", "cabin_class", default="ECONOMY")
@click.option("--stops", default="ANY")
@click.option("--airlines", multiple=True)
@click.option("--monday", is_flag=True)
@click.option("--tuesday", is_flag=True)
@click.option("--wednesday", is_flag=True)
@click.option("--thursday", is_flag=True)
@click.option("--friday", is_flag=True)
@click.option("--saturday", is_flag=True)
@click.option("--sunday", is_flag=True)
@click.pass_context
def search(ctx, origin, destination, from_date, to_date, duration, round_trip,
           cabin_class, stops, airlines, monday, tuesday, wednesday, thursday,
           friday, saturday, sunday):
    """Find cheapest dates in a range.

    ORIGIN and DESTINATION are IATA airport codes.
    """
    fmt, output_path, dry_run = get_ctx_opts(ctx)

    if dry_run:
        emit(
            {"origin": origin.upper(), "destination": destination.upper(),
             "from": from_date, "to": to_date, "duration": duration},
            {"command": "dates.search", "dry_run": True},
            fmt, output_path,
        )
        return

    try:
        results = search_dates(
            origin=origin,
            destination=destination,
            from_date=from_date,
            to_date=to_date,
            duration=duration,
            is_round_trip=round_trip,
            cabin_class=cabin_class,
            max_stops=stops,
            airlines=list(airlines) if airlines else None,
        )

        # Apply day-of-week filters
        day_flags = [monday, tuesday, wednesday, thursday, friday, saturday, sunday]
        if any(day_flags):
            allowed_days = {i for i, flag in enumerate(day_flags) if flag}
            filtered = []
            for r in results:
                date_str = r.get("date") or r.get("departure_date")
                if date_str:
                    dt = datetime.strptime(date_str, "%Y-%m-%d")
                    if dt.weekday() in allowed_days:
                        filtered.append(r)
            results = filtered

        metadata = {
            "origin": origin.upper(),
            "destination": destination.upper(),
            "from_date": from_date,
            "to_date": to_date,
            "result_count": len(results),
        }
        emit(results, metadata, fmt, output_path)
    except GFlightsError as e:
        handle_error(e)


@dates.command()
@click.argument("origin")
@click.argument("destination")
@click.option("--from", "from_date", required=True, help="Start date (YYYY-MM-DD)")
@click.option("--to", "to_date", required=True, help="End date (YYYY-MM-DD)")
@click.option("--duration", "-d", default=None, type=int, help="Trip duration in days")
@click.option("--round-trip", "-R", is_flag=True)
@click.option("--class", "cabin_class", default="ECONOMY")
@click.option("--stops", default="ANY")
@click.option("--airlines", multiple=True)
@click.option("--top", "-n", default=5, type=int, help="Number of cheapest results")
@click.pass_context
def cheapest(ctx, origin, destination, from_date, to_date, duration, round_trip,
             cabin_class, stops, airlines, top):
    """Find the N cheapest dates for a route.

    Wraps dates search and returns results sorted by price.
    """
    fmt, output_path, dry_run = get_ctx_opts(ctx)

    if dry_run:
        emit(
            {"origin": origin.upper(), "destination": destination.upper(),
             "from": from_date, "to": to_date, "top": top},
            {"command": "dates.cheapest", "dry_run": True},
            fmt, output_path,
        )
        return

    try:
        results = search_dates(
            origin=origin,
            destination=destination,
            from_date=from_date,
            to_date=to_date,
            duration=duration,
            is_round_trip=round_trip,
            cabin_class=cabin_class,
            max_stops=stops,
            airlines=list(airlines) if airlines else None,
        )

        results.sort(key=lambda r: r.get("price", float("inf")))
        results = results[:top]

        metadata = {
            "origin": origin.upper(),
            "destination": destination.upper(),
            "from_date": from_date,
            "to_date": to_date,
            "result_count": len(results),
        }
        emit(results, metadata, fmt, output_path)
    except GFlightsError as e:
        handle_error(e)
