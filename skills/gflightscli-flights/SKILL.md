# gflightscli — Flights

Search and compare flights on specific dates.

## flights search

```bash
gflightscli flights search ORIGIN DEST DATE [OPTIONS]
```

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| ORIGIN | string | yes | IATA code (e.g. SEA) |
| DEST | string | yes | IATA code (e.g. JFK) |
| DATE | string | yes | YYYY-MM-DD |
| --return-date | string | no | Return date YYYY-MM-DD |
| --class | string | no | ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST |
| --stops | string | no | ANY, NON_STOP, ONE_STOP_OR_FEWER, TWO_OR_FEWER_STOPS |
| --sort | string | no | CHEAPEST, DURATION, DEPARTURE_TIME, ARRIVAL_TIME |
| --airlines | string | no | Repeatable airline IATA codes |
| --top | int | no | Number of results (default: 10) |

### Examples

```bash
# One-way economy, cheapest
gflightscli flights search SEA JFK 2026-04-01

# Round-trip, non-stop, business
gflightscli flights search SEA LHR 2026-04-01 --return-date 2026-04-10 --class BUSINESS --stops NON_STOP

# Table output
gflightscli flights search SEA JFK 2026-04-01 --format table
```

## flights compare

Compare prices across multiple departure dates.

```bash
gflightscli flights compare ORIGIN DEST DATE1 DATE2 [DATE3...] [OPTIONS]
```

Returns an array with cheapest price per date for quick comparison.

### Example

```bash
gflightscli flights compare SEA JFK 2026-04-01 2026-04-02 2026-04-03 --top 1
```

Output includes `cheapest_price` per date for easy sorting.
