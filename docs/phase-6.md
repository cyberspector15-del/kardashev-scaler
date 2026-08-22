# Phase 6 — Overview Restructure and Dedicated Controls

## Navigation mapping

- **Overview:** educational Kardashev Scale explainer and scroll story.
- **Tracker Control:** standalone NASA-powered fixed-versus-tracked panel comparison.
- **Kardashev Progress:** standalone Earth-scale value, logo fill, session gain, and projection.
- **Sun Position:** standalone live azimuth, elevation, and optimal tilt display with 60-second refresh.
- **Usage Intelligence, Absorption Optimization, Distribution Logic, Recommendation Engine:** unchanged independent Phase 4 pages.

Latitude and longitude remain global in the dashboard top bar and feed every location-aware page.

## Overview structure

1. A short plain-language explanation of Types I, II, and III and Earth’s approximate 0.73 value.
2. A 300vh scroll container with a sticky viewport, large galactic-civilization heading, and active Type I/II/III rows. Scroll progress uses 33% and 66% thresholds.
3. A concise explanation of the project, why solar optimisation matters, and a step-by-step use path.

## Media placeholders

The monochrome placeholders are the three `div`s with IDs `media-1`, `media-2`, and `media-3` in [Dashboard.tsx](../frontend/src/pages/Dashboard.tsx). Their active class is controlled by scroll state and their opacity transition is styled in `frontend/src/index.css` under `.story-media-layer`. To add grayscale MP4 media later, replace each placeholder with a video element while preserving its ID and `active` class pattern; no scroll logic needs to change.
