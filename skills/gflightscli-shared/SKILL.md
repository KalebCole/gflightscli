# gflightscli — Shared Reference

## Install

```bash
cd /path/to/gflightscli
pip install -e .
```

No API keys or authentication needed. The `fli` library calls Google Flights directly.

## Global Flags

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--format` | `json\|table\|yaml\|csv` | `json` | Output format |
| `--dry-run` | flag | off | Show params without calling API |
| `--verbose` | flag | off | Request details on stderr |
| `--output PATH` | string | stdout | Write to file |
| `--no-color` | flag | off | Disable ANSI colors |

## Output Contract

**Success:**
```json
{"status": "success", "data": {...}, "metadata": {...}}
```

**Error:**
```json
{"status": "error", "error": {"code": 3, "type": "validation_error", "message": "..."}}
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | API Error (Google Flights unreachable or rate-limited) |
| 3 | Validation Error (bad input) |
| 4 | Not Found (no results) |
| 5 | Internal Error |

## Introspection

```bash
gflightscli schema flights.search
gflightscli schema dates.cheapest
gflightscli version
```

## Security

- No credentials stored or transmitted
- Price tracking data stored locally at `~/.gflightscli/tracking.json`
- All output to stdout; informational messages to stderr only
- No network calls in `--dry-run` mode

## Available Commands

- `flights search` / `flights compare`
- `dates search` / `dates cheapest`
- `track add` / `track list` / `track check` / `track remove`
- `airports lookup`
- `schema` / `version`

## Retry & Rate Limiting

The underlying `fli` library handles HTTP retries automatically via `curl_cffi` with backoff. If you hit rate limits:

- Space searches 30-60 seconds apart
- Reduce `--top` to fetch fewer results
- Use `--dry-run` to validate parameters before live calls
- For automated tracking, use 30+ minute intervals between checks

## Environment Variables

- `GFLIGHTSCLI_FORMAT` — default output format (`json`, `table`, `yaml`, `csv`)
- `GFLIGHTSCLI_HOME` — config/tracking directory (default: `~/.gflightscli`)
