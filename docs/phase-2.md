# Phase 2 — Supabase Wiring and Tracker Control Logic

## Supabase setup

1. Create a Supabase project.
2. In its SQL Editor, run `backend/supabase/migrations/20260821_phase_2_tracker.sql`.
3. Copy the project URL and **service-role** key to `backend/.env` as `SUPABASE_URL` and `SUPABASE_KEY`. The service-role key stays on the backend only.
4. Copy the project URL and public anon/publishable key to `frontend/.env` as `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY`.
5. In Supabase Authentication > Providers, keep Email enabled. Email/password is enabled by default; no route requires a logged-in user in this phase.

With backend variables absent, all endpoints still work in demo mode but do not persist data. `session_id` scoring needs Supabase because it reads a stored session.

## Schema

- `energy_readings`: timestamped location, GHI/DNI irradiance, panel orientation, optional output, and `fixed` / `tracked` mode.
- `tracker_sessions`: optional auth user, period, location, fixed and tracked totals, and gain percentage.
- `kardashev_progress`: computed Kardashev score linked to a session when one is available (raw demo scores are allowed without one).

All tables use UUID primary keys. Row-level security is enabled; the server service-role key performs writes while authentication remains optional.

## API endpoints

### `POST /api/tracker/sun-position`

```json
{"latitude": 28.6139, "longitude": 77.2090, "timestamp": "2026-08-21T06:00:00Z"}
```

```json
{"solar_azimuth": 82.14, "solar_elevation": 38.7, "optimal_panel_tilt_angle": 51.3}
```

### `POST /api/tracker/nasa-irradiance`

```json
{"latitude": 28.6139, "longitude": 77.2090, "start_date": "2026-08-01", "end_date": "2026-08-03"}
```

```json
{"location":{"latitude":28.6139,"longitude":77.209},"readings":[{"date":"2026-08-01","ghi_kwh_m2_day":5.3,"dni_kwh_m2_day":4.1,"dhi_kwh_m2_day":1.2}]}
```

The NASA POWER call has a 10-second timeout. Failures return HTTP 503 with a retryable message. Dates must be from 1981 through today and no more than 366 days apart.

### `POST /api/tracker/compare`

```json
{"latitude":28.6139,"longitude":77.209,"start_date":"2026-08-01","end_date":"2026-08-03","panel_specs":{"area_m2":2,"efficiency_pct":22}}
```

```json
{"fixed_output_kwh":5.7421,"tracked_output_kwh":7.1032,"efficiency_gain_pct":23.7,"hourly_breakdown":[{"timestamp":"2026-08-01T06:00:00+00:00","fixed_output_kwh":0.12,"tracked_output_kwh":0.17}],"session_id":"uuid-or-null-in-demo-mode"}
```

NASA supplies daily irradiation. The service allocates each daily total across daylight hours according to solar elevation and uses pvlib plane-of-array irradiance to compare a fixed latitude tilt with a two-axis sun-following panel.

### `POST /api/tracker/kardashev-score`

```json
{"session_id":"tracker-session-uuid"}
```

```json
{"earth_kardashev_value":0.7305,"session_efficiency_gain_pct":23.7,"projected_k_shift":0.0002,"projection":{"label":"Estimate: applies this session's tracking gain to all current global solar PV; not a measured Kardashev change.","projected_kardashev_value":0.7307,"global_solar_capacity_tw":2.2,"global_solar_capacity_factor_assumption":0.2},"progress_id":"uuid"}
```

This endpoint deliberately does **not** assign a Kardashev score to an individual panel or tracker session. Sagan's formula, `K = (log10(P watts) - 6) / 10`, is a civilization-wide power scale; applying it to a panel produces a negative value with no scientific interpretation.

Instead, `earth_kardashev_value` is calculated from 2024 global primary energy use of 176,737 TWh/year (about 20.2 TW average), from [Our World in Data's global energy dataset](https://ourworldindata.org/energy-production-consumption), which cites the Energy Institute Statistical Review. The session's measured gain is used only for the explicitly labelled `projection`: it applies that percentage to the IEA's reported 2.2 TW global installed solar PV capacity at end-2024 ([IEA Global Energy Review 2025](https://www.iea.org/reports/global-energy-review-2025/electricity)), using a stated 20% global capacity-factor assumption. It is an estimate of potential additional output, not a measured change in civilization-scale energy use.
