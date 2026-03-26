"""CLI integration tests using Click's CliRunner."""

import json

from click.testing import CliRunner

from gflightscli.cli import cli


def test_version_command():
    runner = CliRunner()
    result = runner.invoke(cli, ["version"])
    assert result.exit_code == 0
    parsed = json.loads(result.output)
    assert parsed["status"] == "success"
    assert "version" in parsed["data"]


def test_schema_flights_search():
    runner = CliRunner()
    result = runner.invoke(cli, ["schema", "flights.search"])
    assert result.exit_code == 0
    parsed = json.loads(result.output)
    assert parsed["status"] == "success"
    assert "positional" in parsed["data"]


def test_schema_unknown_resource():
    runner = CliRunner()
    result = runner.invoke(cli, ["schema", "nonexistent.thing"])
    # handle_error calls sys.exit which CliRunner catches
    assert result.exit_code != 0
    parsed = json.loads(result.output)
    assert parsed["status"] == "error"


def test_flights_search_dry_run():
    runner = CliRunner()
    result = runner.invoke(cli, ["--dry-run", "flights", "search", "SEA", "JFK", "2026-04-01"])
    assert result.exit_code == 0
    parsed = json.loads(result.output)
    assert parsed["status"] == "success"
    assert parsed["metadata"]["dry_run"] is True
    assert parsed["data"]["origin"] == "SEA"


def test_dates_search_dry_run():
    runner = CliRunner()
    result = runner.invoke(cli, [
        "--dry-run", "dates", "search", "SEA", "JFK",
        "--from", "2026-04-01", "--to", "2026-05-01"
    ])
    assert result.exit_code == 0
    parsed = json.loads(result.output)
    assert parsed["metadata"]["dry_run"] is True


def test_dates_cheapest_dry_run():
    runner = CliRunner()
    result = runner.invoke(cli, [
        "--dry-run", "dates", "cheapest", "SEA", "JFK",
        "--from", "2026-04-01", "--to", "2026-05-01"
    ])
    assert result.exit_code == 0
    parsed = json.loads(result.output)
    assert parsed["metadata"]["dry_run"] is True


def test_flights_compare_dry_run():
    runner = CliRunner()
    result = runner.invoke(cli, [
        "--dry-run", "flights", "compare", "SEA", "JFK",
        "2026-04-01", "2026-04-02"
    ])
    assert result.exit_code == 0
    parsed = json.loads(result.output)
    assert parsed["metadata"]["dry_run"] is True


def test_airports_lookup_invalid():
    """Lookup with gibberish should exit 4 (not found)."""
    runner = CliRunner()
    result = runner.invoke(cli, ["airports", "lookup", "xyzzyplugh99"])
    assert result.exit_code == 4
    parsed = json.loads(result.output)
    assert parsed["status"] == "error"
    assert parsed["error"]["code"] == 4


def test_airports_lookup_valid():
    runner = CliRunner()
    result = runner.invoke(cli, ["airports", "lookup", "JFK"])
    assert result.exit_code == 0
    parsed = json.loads(result.output)
    assert parsed["status"] == "success"
    assert len(parsed["data"]) > 0


def test_format_table():
    """Table format should not crash on dry-run data."""
    runner = CliRunner()
    result = runner.invoke(cli, [
        "--format", "table", "--dry-run", "flights", "search", "SEA", "JFK", "2026-04-01"
    ])
    assert result.exit_code == 0
    assert "origin" in result.output.lower()


def test_format_yaml():
    runner = CliRunner()
    result = runner.invoke(cli, [
        "--format", "yaml", "--dry-run", "flights", "search", "SEA", "JFK", "2026-04-01"
    ])
    assert result.exit_code == 0
    assert "status: success" in result.output


def test_format_csv():
    runner = CliRunner()
    result = runner.invoke(cli, [
        "--format", "csv", "--dry-run", "flights", "search", "SEA", "JFK", "2026-04-01"
    ])
    assert result.exit_code == 0


def test_output_to_file(tmp_path):
    outfile = str(tmp_path / "out.json")
    runner = CliRunner()
    result = runner.invoke(cli, [
        "--output", outfile, "--dry-run", "flights", "search", "SEA", "JFK", "2026-04-01"
    ])
    assert result.exit_code == 0
    with open(outfile) as f:
        parsed = json.load(f)
    assert parsed["status"] == "success"
