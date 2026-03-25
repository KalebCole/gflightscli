# gflightscli

JSON-first, agent-friendly Google Flights CLI wrapping the [fli](https://pypi.org/project/flights/) library.

## Install

```bash
pip install -e .
```

No API keys needed — fli reverse-engineers Google Flights directly.

## Quick Start

```bash
# Search flights SEA → JFK on April 1st
gflightscli flights search SEA JFK 2026-04-01

# Find cheapest dates in a range
gflightscli dates cheapest SEA EZE --from 2026-06-01 --to 2026-08-01 --top 5

# Look up an airport code
gflightscli airports lookup seattle
```

## Why gflightscli?

**For humans:** Get flight prices from the terminal without opening a browser. Compare dates, track prices, pipe results into other tools.

**For agents:** Every command outputs structured JSON to stdout. No scraping, no HTML parsing. Deterministic exit codes. Built for automation.

## Command Reference

### `flights search ORIGIN DEST DATE`

Search flights for a specific date.

```bash
gflightscli flights search SEA JFK 2026-04-01 --class ECONOMY --stops NON_STOP --sort CHEAPEST
gflightscli flights search SEA LHR 2026-04-01 --return-date 2026-04-10 --top 5
```

**Options:** `--return-date`, `--class`, `--stops`, `--sort`, `--airlines`, `--top`

### `flights compare ORIGIN DEST DATE1 DATE2 ...`

Compare flights across multiple dates.

```bash
gflightscli flights compare SEA JFK 2026-04-01 2026-04-02 2026-04-03
```

### `dates search ORIGIN DEST --from DATE --to DATE`

Find cheapest dates in a range.

```bash
gflightscli dates search SEA EZE --from 2026-06-01 --to 2026-08-01 --friday --saturday
```

**Options:** `--duration`, `--round-trip`, `--class`, `--stops`, `--airlines`, `--monday` through `--sunday`

### `dates cheapest ORIGIN DEST --from DATE --to DATE`

Top N cheapest dates for a route.

```bash
gflightscli dates cheapest SEA EZE --from 2026-06-01 --to 2026-08-01 --top 3
```

### `airports lookup QUERY`

Look up airports by IATA code or city name.

```bash
gflightscli airports lookup "seattle"
gflightscli airports lookup SEA
```

### `track add/list/check/remove`

Price tracking with persistent storage.

```bash
gflightscli track add SEA EZE 2026-11-15 --below 500 --return-date 2026-11-30
gflightscli track list
gflightscli track check
gflightscli track remove abc123
```

### `schema RESOURCE.METHOD`

Introspect parameters for any command.

```bash
gflightscli schema flights.search
```

### `version`

```bash
gflightscli version
```

## Helper Commands

| Command | Description |
|---------|-------------|
| `flights compare` | Compare prices across multiple dates |
| `dates cheapest` | Find the N cheapest dates in a range |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | API Error |
| 3 | Validation Error |
| 4 | Not Found |
| 5 | Internal Error |

## Output Formats

```bash
gflightscli flights search SEA JFK 2026-04-01 --format json    # default
gflightscli flights search SEA JFK 2026-04-01 --format table
gflightscli flights search SEA JFK 2026-04-01 --format yaml
gflightscli flights search SEA JFK 2026-04-01 --format csv
```

All formats wrap data in a success/error envelope. JSON output:

```json
{
  "status": "success",
  "data": [...],
  "metadata": { "origin": "SEA", "destination": "JFK", ... }
}
```

## Global Flags

| Flag | Description |
|------|-------------|
| `--format json\|table\|yaml\|csv` | Output format (default: json) |
| `--dry-run` | Show search params without calling API |
| `--verbose` | Show request details on stderr |
| `--output PATH` | Write output to file |
| `--no-color` | Disable ANSI colors |

## Price Tracking

Tracked routes are stored in `~/.gflightscli/tracking.json`. Use with cron for automated alerts:

```bash
# Add a price alert
gflightscli track add SEA EZE 2026-11-15 --below 500

# Check via cron (pair with notification tool)
*/30 * * * * gflightscli track check --format json | jq '.data[] | select(.below_threshold)'
```

## Skills for AI Agents

Six SKILL.md files in `skills/` provide structured instructions for AI agents:

- `gflightscli-shared` — install, global flags, output contract, exit codes
- `gflightscli-flights` — flight search reference and examples
- `gflightscli-dates` — date search and cheapest helper
- `gflightscli-track` — price tracking CRUD
- `recipe-trip-planner` — multi-step trip planning workflow
- `recipe-price-monitor` — automated price monitoring setup

## Development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -v
ruff check src/ tests/
```
