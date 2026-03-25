# gflightscli — Price Tracking

Track flight routes and check for price drops.

## Storage

Tracking data: `~/.gflightscli/tracking.json`

## Commands

### track add

```bash
gflightscli track add ORIGIN DEST DATE --below PRICE [OPTIONS]
```

| Param | Required | Description |
|-------|----------|-------------|
| ORIGIN | yes | IATA code |
| DEST | yes | IATA code |
| DATE | yes | YYYY-MM-DD |
| --below | yes | Price threshold (alert when price ≤ this) |
| --return-date | no | Return date |
| --class | no | Cabin class (default: ECONOMY) |
| --stops | no | Max stops (default: ANY) |

### track list

```bash
gflightscli track list
```

### track check

```bash
gflightscli track check              # Check all tracked routes
gflightscli track check --id abc123  # Check specific track
```

Returns current prices and whether each is below threshold.

### track remove

```bash
gflightscli track remove TRACK_ID
```

## Cron Integration

```bash
# Check every 30 minutes, filter alerts
*/30 * * * * gflightscli track check | jq '.data[] | select(.below_threshold)' >> /tmp/flight-alerts.json

# OpenClaw cron example
openclaw crons add --label "flight-check" --schedule "0 */6 * * *" \
  --prompt "Run gflightscli track check and notify me of any below-threshold prices"
```

## Example Workflow

```bash
# 1. Add tracking
gflightscli track add SEA EZE 2026-11-15 --below 500 --return-date 2026-11-30

# 2. Verify
gflightscli track list

# 3. Check prices
gflightscli track check

# 4. Remove when done
gflightscli track remove abc123
```
