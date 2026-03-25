# gflightscli — Dates

Search for cheapest travel dates across a range.

## dates search

```bash
gflightscli dates search ORIGIN DEST --from DATE --to DATE [OPTIONS]
```

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| ORIGIN | string | yes | IATA code |
| DEST | string | yes | IATA code |
| --from | string | yes | Range start YYYY-MM-DD |
| --to | string | yes | Range end YYYY-MM-DD |
| --duration | int | no | Trip duration in days |
| --round-trip | flag | no | Round-trip search |
| --class | string | no | Cabin class |
| --stops | string | no | Max stops |
| --airlines | string | no | Airline filters |
| --monday..--sunday | flags | no | Day-of-week filters |

### Day-of-week Filtering

Combine day flags to only show specific days:

```bash
# Only Friday and Saturday departures
gflightscli dates search SEA EZE --from 2026-06-01 --to 2026-08-01 --friday --saturday
```

## dates cheapest

Returns the top N cheapest dates, sorted by price.

```bash
gflightscli dates cheapest ORIGIN DEST --from DATE --to DATE --top N
```

### Examples

```bash
# 3 cheapest dates SEA→EZE in summer
gflightscli dates cheapest SEA EZE --from 2026-06-01 --to 2026-08-01 --top 3

# Cheapest weekend dates
gflightscli dates search SEA EZE --from 2026-06-01 --to 2026-08-01 --friday --saturday --format table
```
