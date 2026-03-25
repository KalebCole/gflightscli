# Recipe: Trip Planner

Multi-step workflow to find the best flight for a trip.

## When to Use

User wants to plan a trip and needs a recommendation with tradeoffs (price vs convenience vs timing).

## Steps

### 1. Find cheapest dates

```bash
gflightscli dates cheapest ORIGIN DEST --from START --to END --top 5
```

Parse the result. Note the 5 cheapest dates and their prices.

### 2. Compare top dates with full flight details

Take the top 3-5 dates and run:

```bash
gflightscli flights compare ORIGIN DEST DATE1 DATE2 DATE3 --top 3
```

### 3. Analyze tradeoffs

For each date, evaluate:
- **Price** — cheapest option
- **Duration** — shortest travel time
- **Stops** — non-stop vs connecting
- **Times** — departure/arrival convenience

### 4. Present recommendation

Format as a brief comparison:
- Best price: DATE at $X (DURATION, STOPS stops)
- Best convenience: DATE at $X (non-stop, reasonable times)
- Best balance: DATE at $X (explain why)

## Example

```bash
# Step 1: Find cheap dates SEA→EZE in November
gflightscli dates cheapest SEA EZE --from 2026-11-01 --to 2026-11-30 --top 5

# Step 2: Compare top 3
gflightscli flights compare SEA EZE 2026-11-05 2026-11-12 2026-11-19 --top 3

# Step 3: Present tradeoffs to user
```

## Tips

- If user has flexible dates, use `dates cheapest` first
- If user has a fixed date, skip to `flights search`
- Always mention if non-stop options exist but cost more
- Round-trip: use `--return-date` on flights search
