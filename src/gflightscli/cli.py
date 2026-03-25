"""CLI entry point — Click group with global flags."""

from __future__ import annotations

import json
import sys

import click

from gflightscli import __version__
from gflightscli.commands.airports import airports
from gflightscli.commands.dates import dates
from gflightscli.commands.flights import flights
from gflightscli.commands.track import track
from gflightscli.lib.errors import GFlightsError, InternalError, handle_error


@click.group()
@click.option("--format", "-f", "fmt", default="json",
              type=click.Choice(["json", "table", "yaml", "csv"]),
              help="Output format")
@click.option("--dry-run", is_flag=True, help="Show params without calling API")
@click.option("--verbose", is_flag=True, help="Show request details on stderr")
@click.option("--output", "-o", default=None, type=click.Path(), help="Write output to file")
@click.option("--no-color", is_flag=True, help="Disable ANSI colors")
@click.pass_context
def cli(ctx, fmt, dry_run, verbose, output, no_color):
    """gflightscli — JSON-first Google Flights CLI."""
    ctx.ensure_object(dict)
    ctx.obj["format"] = fmt
    ctx.obj["dry_run"] = dry_run
    ctx.obj["verbose"] = verbose
    ctx.obj["output"] = output
    ctx.obj["no_color"] = no_color


cli.add_command(flights)
cli.add_command(dates)
cli.add_command(track)
cli.add_command(airports)


@cli.command()
def version():
    """Print version."""
    click.echo(json.dumps({"status": "success", "data": {"version": __version__}}))


SCHEMA_DEFINITIONS = {
    "flights.search": {
        "positional": ["ORIGIN", "DESTINATION", "DATE"],
        "options": {
            "--return-date": "Return date (YYYY-MM-DD)",
            "--class": "Cabin class: ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST",
            "--stops": "Max stops: ANY, NON_STOP, ONE_STOP_OR_FEWER, TWO_OR_FEWER_STOPS",
            "--sort": "Sort: CHEAPEST, DURATION, DEPARTURE_TIME, ARRIVAL_TIME",
            "--airlines": "Airline IATA codes (repeatable)",
            "--top": "Number of results (default: 10)",
        },
    },
    "flights.compare": {
        "positional": ["ORIGIN", "DESTINATION", "DATES..."],
        "options": {
            "--class": "Cabin class",
            "--stops": "Max stops",
            "--sort": "Sort order",
            "--airlines": "Airline codes",
            "--top": "Results per date (default: 3)",
        },
    },
    "dates.search": {
        "positional": ["ORIGIN", "DESTINATION"],
        "options": {
            "--from": "Start date (YYYY-MM-DD, required)",
            "--to": "End date (YYYY-MM-DD, required)",
            "--duration": "Trip duration in days",
            "--round-trip": "Round-trip search",
            "--class": "Cabin class",
            "--stops": "Max stops",
            "--airlines": "Airline codes",
            "--monday/--tuesday/.../--sunday": "Day-of-week filters",
        },
    },
    "dates.cheapest": {
        "positional": ["ORIGIN", "DESTINATION"],
        "options": {
            "--from": "Start date (required)",
            "--to": "End date (required)",
            "--duration": "Trip duration in days",
            "--round-trip": "Round-trip",
            "--class": "Cabin class",
            "--stops": "Max stops",
            "--top": "Number of cheapest results (default: 5)",
        },
    },
    "track.add": {
        "positional": ["ORIGIN", "DESTINATION", "DATE"],
        "options": {
            "--return-date": "Return date",
            "--below": "Price threshold (required)",
            "--class": "Cabin class",
            "--stops": "Max stops",
        },
    },
    "track.list": {"positional": [], "options": {}},
    "track.check": {"options": {"--id": "Check specific track by ID"}},
    "track.remove": {"positional": ["TRACK_ID"]},
    "airports.lookup": {"positional": ["QUERY"]},
}


@cli.command()
@click.argument("resource_method")
def schema(resource_method):
    """Show accepted parameters for a resource.method.

    Example: gflightscli schema flights.search
    """
    defn = SCHEMA_DEFINITIONS.get(resource_method)
    if not defn:
        handle_error(
            GFlightsError(
                f"Unknown resource.method '{resource_method}'. "
                f"Available: {', '.join(sorted(SCHEMA_DEFINITIONS.keys()))}"
            )
        )
        return
    click.echo(json.dumps({"status": "success", "data": defn}, indent=2))


def main():
    """Entry point with top-level error handling."""
    try:
        cli(standalone_mode=False)
    except SystemExit as e:
        sys.exit(e.code)
    except GFlightsError as e:
        handle_error(e)
    except click.exceptions.ClickException as e:
        handle_error(InternalError(str(e)))
    except Exception as e:
        handle_error(InternalError(f"Unexpected error: {e}"))


if __name__ == "__main__":
    main()
