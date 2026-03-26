"""Airport IATA code lookup."""

from __future__ import annotations

import click

from gflightscli.lib.errors import GFlightsError, handle_error
from gflightscli.lib.fli_bridge import lookup_airports
from gflightscli.lib.output import emit, get_ctx_opts


@click.group()
def airports():
    """Airport lookup utilities."""
    pass


@airports.command()
@click.argument("query")
@click.pass_context
def lookup(ctx, query):
    """Look up airports by IATA code or city name.

    QUERY can be a partial code (e.g. "SEA") or city name (e.g. "seattle").
    """
    fmt, output_path, _ = get_ctx_opts(ctx)

    try:
        results = lookup_airports(query)
        emit(results, {"query": query, "result_count": len(results)}, fmt, output_path)
    except GFlightsError as e:
        handle_error(e)
