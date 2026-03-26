"""flights search + compare commands."""

from __future__ import annotations

import click

from gflightscli.lib.errors import GFlightsError, handle_error
from gflightscli.lib.fli_bridge import search_flights
from gflightscli.lib.output import emit, get_ctx_opts


@click.group()
def flights():
    """Search and compare flights."""
    pass


@flights.command()
@click.argument("origin")
@click.argument("destination")
@click.argument("date")
@click.option("--return-date", "-r", default=None, help="Return date (YYYY-MM-DD)")
@click.option("--class", "cabin_class", default="ECONOMY",
              help="Cabin class: ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST")
@click.option("--stops", default="ANY",
              help="Max stops: ANY, NON_STOP, ONE_STOP_OR_FEWER, TWO_OR_FEWER_STOPS")
@click.option("--sort", default="CHEAPEST",
              help="Sort by: CHEAPEST, DURATION, DEPARTURE_TIME, ARRIVAL_TIME")
@click.option("--airlines", multiple=True, help="Airline IATA codes")
@click.option("--top", default=10, help="Number of results", type=int)
@click.pass_context
def search(ctx, origin, destination, date, return_date, cabin_class, stops, sort, airlines, top):
    """Search flights for a specific date.

    ORIGIN and DESTINATION are IATA airport codes (e.g. SEA, JFK).
    DATE is departure date in YYYY-MM-DD format.
    """
    fmt, output_path, dry_run = get_ctx_opts(ctx)

    params = {
        "origin": origin.upper(),
        "destination": destination.upper(),
        "date": date,
        "return_date": return_date,
        "cabin_class": cabin_class,
        "stops": stops,
        "sort": sort,
        "airlines": list(airlines) if airlines else None,
        "top": top,
    }

    if dry_run:
        emit(params, {"command": "flights.search", "dry_run": True}, fmt, output_path)
        return

    try:
        results = search_flights(
            origin=origin,
            destination=destination,
            departure_date=date,
            return_date=return_date,
            cabin_class=cabin_class,
            max_stops=stops,
            sort_by=sort,
            airlines=list(airlines) if airlines else None,
            top_n=top,
        )
        metadata = {
            "origin": origin.upper(),
            "destination": destination.upper(),
            "date": date,
            "return_date": return_date,
            "result_count": len(results),
        }
        emit(results, metadata, fmt, output_path)
    except GFlightsError as e:
        handle_error(e)


@flights.command()
@click.argument("origin")
@click.argument("destination")
@click.argument("dates", nargs=-1, required=True)
@click.option("--class", "cabin_class", default="ECONOMY")
@click.option("--stops", default="ANY")
@click.option("--sort", default="CHEAPEST")
@click.option("--airlines", multiple=True)
@click.option("--top", default=3, type=int, help="Results per date")
@click.pass_context
def compare(ctx, origin, destination, dates, cabin_class, stops, sort, airlines, top):
    """Compare flights across multiple dates.

    Pass multiple dates: gflightscli flights compare SEA JFK 2026-04-01 2026-04-02 2026-04-03
    """
    fmt, output_path, dry_run = get_ctx_opts(ctx)

    if dry_run:
        emit(
            {"dates": list(dates), "origin": origin.upper(), "destination": destination.upper()},
            {"command": "flights.compare", "dry_run": True},
            fmt,
            output_path,
        )
        return

    comparison = []
    for date in dates:
        try:
            results = search_flights(
                origin=origin,
                destination=destination,
                departure_date=date,
                cabin_class=cabin_class,
                max_stops=stops,
                sort_by=sort,
                airlines=list(airlines) if airlines else None,
                top_n=top,
            )
            best = results[0] if results else None
            comparison.append({
                "date": date,
                "cheapest_price": best["price"] if best else None,
                "results": results,
            })
        except GFlightsError as e:
            comparison.append({
                "date": date,
                "cheapest_price": None,
                "error": e.message,
                "results": [],
            })

    metadata = {
        "origin": origin.upper(),
        "destination": destination.upper(),
        "dates_compared": len(dates),
    }
    emit(comparison, metadata, fmt, output_path)
