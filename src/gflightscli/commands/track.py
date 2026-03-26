"""Price tracking CRUD commands."""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

import click

from gflightscli.lib.errors import GFlightsError, NotFoundError, ValidationError, handle_error
from gflightscli.lib.fli_bridge import search_flights
from gflightscli.lib.output import emit


TRACKING_DIR = Path.home() / ".gflightscli"
TRACKING_FILE = TRACKING_DIR / "tracking.json"


def _load_tracks() -> list[dict]:
    if not TRACKING_FILE.exists():
        return []
    with open(TRACKING_FILE) as f:
        data = json.load(f)
    return data.get("tracks", [])


def _save_tracks(tracks: list[dict]) -> None:
    TRACKING_DIR.mkdir(parents=True, exist_ok=True)
    with open(TRACKING_FILE, "w") as f:
        json.dump({"tracks": tracks}, f, indent=2)


@click.group()
def track():
    """Price tracking for flight routes."""
    pass


@track.command()
@click.argument("origin")
@click.argument("destination")
@click.argument("date")
@click.option("--return-date", "-r", default=None, help="Return date (YYYY-MM-DD)")
@click.option("--below", "-b", required=True, type=float, help="Price threshold to alert on")
@click.option("--class", "cabin_class", default="ECONOMY")
@click.option("--stops", default="ANY")
@click.pass_context
def add(ctx, origin, destination, date, return_date, below, cabin_class, stops):
    """Add a route to price tracking.

    Tracks ORIGIN→DESTINATION on DATE and alerts when price drops below --below.
    """
    fmt = ctx.obj.get("format", "json")
    output_path = ctx.obj.get("output")

    tracks = _load_tracks()
    new_track = {
        "id": str(uuid.uuid4())[:8],
        "origin": origin.upper(),
        "destination": destination.upper(),
        "date": date,
        "return_date": return_date,
        "below": below,
        "filters": {"class": cabin_class, "stops": stops},
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_checked": None,
        "last_price": None,
    }
    tracks.append(new_track)
    _save_tracks(tracks)

    emit(new_track, {"command": "track.add"}, fmt, output_path)


@track.command("list")
@click.pass_context
def list_tracks(ctx):
    """Show all tracked routes."""
    fmt = ctx.obj.get("format", "json")
    output_path = ctx.obj.get("output")

    tracks = _load_tracks()
    emit(tracks, {"command": "track.list", "count": len(tracks)}, fmt, output_path)


@track.command()
@click.option("--id", "track_id", default=None, help="Check a specific track by ID")
@click.pass_context
def check(ctx, track_id):
    """Run price check on tracked routes."""
    fmt = ctx.obj.get("format", "json")
    output_path = ctx.obj.get("output")

    tracks = _load_tracks()
    if track_id:
        tracks = [t for t in tracks if t["id"] == track_id]
        if not tracks:
            handle_error(NotFoundError(f"No track with id '{track_id}'."))
            return

    results = []
    all_tracks = _load_tracks()

    for t in tracks:
        try:
            flights = search_flights(
                origin=t["origin"],
                destination=t["destination"],
                departure_date=t["date"],
                return_date=t.get("return_date"),
                cabin_class=t["filters"].get("class", "ECONOMY"),
                max_stops=t["filters"].get("stops", "ANY"),
                top_n=1,
            )
            current_price = flights[0]["price"] if flights else None
        except GFlightsError:
            current_price = None

        # Update tracking state
        for at in all_tracks:
            if at["id"] == t["id"]:
                at["last_checked"] = datetime.now(timezone.utc).isoformat()
                at["last_price"] = current_price

        below_threshold = current_price is not None and current_price <= t["below"]
        results.append({
            "id": t["id"],
            "origin": t["origin"],
            "destination": t["destination"],
            "date": t["date"],
            "threshold": t["below"],
            "current_price": current_price,
            "below_threshold": below_threshold,
        })

    _save_tracks(all_tracks)
    emit(results, {"command": "track.check", "checked": len(results)}, fmt, output_path)


@track.command()
@click.argument("track_id")
@click.pass_context
def remove(ctx, track_id):
    """Remove a tracked route by ID."""
    fmt = ctx.obj.get("format", "json")
    output_path = ctx.obj.get("output")
    dry_run = ctx.obj.get("dry_run", False)

    tracks = _load_tracks()
    target = [t for t in tracks if t["id"] == track_id]

    if not target:
        handle_error(NotFoundError(f"No track with id '{track_id}'."))
        return

    if dry_run:
        emit(
            target[0],
            {"command": "track.remove", "dry_run": True},
            fmt, output_path,
        )
        return

    tracks = [t for t in tracks if t["id"] != track_id]
    _save_tracks(tracks)
    emit(
        {"removed": track_id},
        {"command": "track.remove"},
        fmt, output_path,
    )
