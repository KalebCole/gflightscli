# Recipe: Price Monitor

Set up automated flight price monitoring with alerts.

## When to Use

User wants to watch a route and get notified when prices drop below a threshold.

## Steps

### 1. Add price tracking

```bash
gflightscli track add ORIGIN DEST DATE --below THRESHOLD [--return-date DATE]
```

### 2. Verify the track was added

```bash
gflightscli track list
```

### 3. Do an initial price check

```bash
gflightscli track check
```

Review current prices. If already below threshold, notify immediately.

### 4. Schedule automated checks

**With OpenClaw cron:**

```bash
openclaw crons add \
  --label "flight-price-monitor" \
  --schedule "0 */6 * * *" \
  --prompt "Run: gflightscli track check --format json. If any result has below_threshold=true, message me with the details. Otherwise stay quiet."
```

**With system cron:**

```bash
# Check every 6 hours, log alerts
0 */6 * * * gflightscli track check | jq -r '.data[] | select(.below_threshold) | "\(.origin)→\(.destination) \(.date): $\(.current_price) (threshold: $\(.threshold))"' >> ~/flight-alerts.log
```

### 5. Clean up when done

```bash
gflightscli track remove TRACK_ID
```

## Example

```bash
# Watch SEA→EZE for November trip, alert below $500
gflightscli track add SEA EZE 2026-11-15 --below 500 --return-date 2026-11-30

# Set up 6-hourly monitoring
openclaw crons add --label "eze-price-watch" --schedule "0 */6 * * *" \
  --prompt "Check flight prices: gflightscli track check. Alert me only if below_threshold is true."

# Later: remove tracking
gflightscli track list  # get the ID
gflightscli track remove abc123
```

## Tips

- Set threshold ~20% below current price for realistic alerts
- Check `track list` periodically to prune expired routes
- Combine with `dates cheapest` to find optimal monitoring dates first
