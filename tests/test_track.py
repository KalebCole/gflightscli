"""Tests for price tracking CRUD."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from gflightscli.commands.track import _load_tracks, _save_tracks, TRACKING_FILE


@pytest.fixture
def tmp_tracking(tmp_path, monkeypatch):
    """Redirect tracking file to a temp directory."""
    import gflightscli.commands.track as track_mod
    tracking_file = tmp_path / "tracking.json"
    monkeypatch.setattr(track_mod, "TRACKING_DIR", tmp_path)
    monkeypatch.setattr(track_mod, "TRACKING_FILE", tracking_file)
    return tracking_file


def test_load_empty(tmp_tracking):
    assert _load_tracks() == []


def test_save_and_load(tmp_tracking):
    tracks = [
        {
            "id": "abc123",
            "origin": "SEA",
            "destination": "JFK",
            "date": "2026-04-01",
            "return_date": None,
            "below": 300,
            "filters": {"class": "ECONOMY", "stops": "ANY"},
            "created_at": "2026-03-25T00:00:00Z",
            "last_checked": None,
            "last_price": None,
        }
    ]
    _save_tracks(tracks)
    loaded = _load_tracks()
    assert len(loaded) == 1
    assert loaded[0]["id"] == "abc123"
    assert loaded[0]["below"] == 300


def test_save_multiple_and_load(tmp_tracking):
    t1 = {"id": "aaa", "origin": "SEA", "destination": "JFK",
           "date": "2026-04-01", "below": 200, "filters": {}}
    t2 = {"id": "bbb", "origin": "LAX", "destination": "LHR",
           "date": "2026-05-01", "below": 500, "filters": {}}
    _save_tracks([t1, t2])
    loaded = _load_tracks()
    assert len(loaded) == 2


def test_remove_track(tmp_tracking):
    tracks = [
        {"id": "keep", "origin": "A"},
        {"id": "remove", "origin": "B"},
    ]
    _save_tracks(tracks)
    remaining = [t for t in _load_tracks() if t["id"] != "remove"]
    _save_tracks(remaining)
    loaded = _load_tracks()
    assert len(loaded) == 1
    assert loaded[0]["id"] == "keep"


def test_track_remove_dry_run(tmp_tracking):
    """--dry-run should show what would be removed without deleting."""
    _save_tracks([{"id": "abc123", "origin": "SEA", "destination": "JFK",
                   "date": "2026-04-01", "below": 300, "filters": {}}])

    from click.testing import CliRunner
    from gflightscli.cli import cli
    runner = CliRunner()
    result = runner.invoke(cli, ["--dry-run", "track", "remove", "abc123"])
    assert result.exit_code == 0
    parsed = json.loads(result.output)
    assert parsed["metadata"]["dry_run"] is True

    # Verify track was NOT actually removed
    assert len(_load_tracks()) == 1


def test_tracking_file_format(tmp_tracking):
    _save_tracks([{"id": "x", "origin": "SEA"}])
    raw = json.loads(tmp_tracking.read_text())
    assert "tracks" in raw
    assert isinstance(raw["tracks"], list)
