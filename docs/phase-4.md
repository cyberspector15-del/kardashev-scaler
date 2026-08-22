# Phase 4 — Intelligence and Optimisation Modules

## Endpoints

### `POST /api/usage/analyze`

Accepts a persisted `session_id`, or raw `captured_kwh`, `consumed_kwh`, and optional hourly `consumption_profile`.

```json
{"captured_kwh":1.5,"consumed_kwh":1,"consumption_profile":[{"hour":0,"demand_kwh":0.5},{"hour":1,"demand_kwh":0.5}]}
```

```json
{"captured_kwh":1.5,"consumed_kwh":1,"waste_kwh":0.5,"deficit_kwh":0,"waste_pct":33.33,"flagged_windows":[{"window":"0","waste_kwh":0.25},{"window":"1","waste_kwh":0.25}],"deficit_windows":[]}
```

Waste is captured energy beyond consumption; deficit is unmet consumption. When a profile is supplied, its `demand_kwh` values must sum to `consumed_kwh`. Tracker output currently supplies only a total, so the service distributes that captured total evenly over the same profile windows and derives **both** aggregate totals from that shared window ledger. Consequently, all `flagged_windows.waste_kwh` values sum exactly to `waste_kwh`; `sum(window waste) - sum(window deficit)` reconciles to `waste_kwh - deficit_kwh`. With no profile, the service uses an even 24-hour demand distribution solely as a transparent demo fallback.

### `POST /api/absorption/zones`

```json
{"center_lat":28.6139,"center_lng":77.209,"radius_km":10,"grid_size":3}
```

```json
{"zones":[{"lat":28.52381,"lng":77.1064,"avg_irradiance":4.7,"panel_density_assumed":0.15,"potential_score":3.995}],"top_recommendation":{"lat":28.52381,"lng":77.1064,"potential_score":3.995}}
```

The service samples daily NASA POWER GHI over a 1–5 × 1–5 grid (maximum 25 points). `potential_score = GHI × (1 - panel density)`. When density is not supplied, it assumes 0.15 to highlight unentered/low-coverage areas. The endpoint retains NASA timeout/failure handling from Phase 2.

### `POST /api/distribution/model`

```json
{"total_captured_kwh":300,"demand_breakdown":{"residential_pct":40,"industrial_pct":40,"agricultural_pct":20}}
```

```json
{"allocations":{"residential_kwh":120,"industrial_kwh":120,"agricultural_kwh":60},"shortfalls":[{"sector":"industrial","shortfall_kwh":100},{"sector":"agricultural","shortfall_kwh":20}]}
```

Captured energy is split in exact proportion to the supplied percentages, which must sum to 100. Placeholder per-run microgrid demand baselines are residential 120 kWh, industrial 220 kWh, and agricultural 80 kWh. They make shortfalls visible in the demo and are explicitly not production demand forecasts; real telemetry should replace them.

### `POST /api/recommendations/generate`

Accepts the previous three endpoint outputs directly, so it works without additional database reads.

```json
{"usage":{"waste_pct":25,"deficit_kwh":0},"absorption":{"top_recommendation":{"lat":28.5,"lng":77.1,"potential_score":4,"panel_density_assumed":0.15}},"distribution":{"shortfalls":[{"sector":"industrial","shortfall_kwh":100}]}}
```

```json
{"recommendations":[{"priority":"high","action":"Add battery storage for surplus windows.","reason":"Captured-energy waste is 25%, above the 20% threshold."}]}
```

## Recommendation rules

1. Waste above 20% → high-priority battery storage recommendation.
2. Any captured-energy deficit → high-priority capture expansion or demand-shifting recommendation.
3. Top absorption zone score above 3 with panel density below 0.3 → medium-priority build-here recommendation.
4. Each distribution shortfall → medium-priority allocation-increase recommendation for that sector.
5. No triggered rules → low-priority measurement/monitoring recommendation.

Rules are sorted high, medium, low and use no ML or hidden weighting.

## Dashboard flow

Tracker Comparison can feed its tracked kWh value directly to Usage Intelligence and Distribution Logic. Usage, Absorption, and Distribution outputs stay available independently and are passed together to Recommendation Engine when present. Each panel has an independent trigger, monochrome loading/error/retry state, and uses bright-to-dim white glow—not colour—to show recommendation priority.
