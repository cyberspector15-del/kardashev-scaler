# Phase 3 — Home Screen and Dashboard Shell

## Routes

- `/`: a full-viewport, pure-black entry screen. The large glowing Kardashev mark is the visual focus, accompanied only by the understated project name and an outlined **Enter** link to the dashboard.
- `/dashboard`: the application shell, with a thin left navigation rail, top location controls, and a responsive overview workspace.

## Dashboard structure

The Overview includes three monochrome panels:

1. **Panel comparison** submits the selected location, date range, area, and efficiency to `POST /api/tracker/compare`. It renders fixed versus tracked energy as white-only comparison bars and shows the calculated gain.
2. **Kardashev Progress** uses the `session_id` returned by comparison to call `POST /api/tracker/kardashev-score`. It presents the Earth-scale value, projection shift, and session gain. The API's “estimate, not measured” language is visibly retained. It will prompt for Supabase configuration when a comparison cannot be stored as a session.
3. **Sun position** calls `POST /api/tracker/sun-position` with the entered location and current timestamp, then refreshes every 60 seconds.

All requests have monochrome loading pulse states and inline error/retry controls. NASA-related failures do not crash the screen.

The navigation also lists Usage Intelligence, Absorption Optimization, Distribution Logic, and Recommendation Engine. They intentionally render a **Coming in Phase 4** placeholder and contain no logic in this phase.

## Logo update

`Logo` now accepts `fillPercent?: number`. It controls the illuminated height of its first bar from 0–100, clamps out-of-range values, and defaults to `73`; all existing usages therefore retain their original appearance. The Kardashev panel passes Earth K × 100 to this prop.

## Screen descriptions

- **Home:** the white ascending-bar logo floats at the center of black space with a restrained breathing glow. “KARDASHEV SCALER” sits below it, followed by one sharp outlined entry control.
- **Dashboard:** an outlined narrow rail frames the left edge. The main view is divided by thin white rules into a control-and-comparison area, an Earth-progress card with the live logo mark, and a wide live-sun readout below. There are no accent colors, rounded cards, marketing text, or non-functional feature screens.
