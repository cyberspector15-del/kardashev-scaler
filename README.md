# Kardashev Scaler

Kardashev Scaler is a Smart India Hackathon SIH1731 solar-energy tracking dashboard. It compares fixed and tracking panels with NASA POWER irradiance and pvlib, then turns the results into practical usage, absorption, distribution, and rule-based recommendation insights.

## Stack

- Frontend: React, Vite, TypeScript, Tailwind CSS
- Backend: FastAPI, pvlib, NASA POWER API, optional Supabase persistence
- Design: strict black/off-white/white-glow visual system and scalable SVG logo

## Run locally

Backend:

```bash
cd backend
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`. The API health check is `http://127.0.0.1:8000/health`.

For optional Supabase persistence, follow [Phase 2](docs/phase-2.md).

## Project phases

1. [Phase 1 — Foundation](docs/phase-1.md)
2. [Phase 2 — Supabase and Tracker Core](docs/phase-2.md)
3. [Phase 3 — Home and Dashboard Shell](docs/phase-3.md)
4. [Phase 4 — Intelligence Modules](docs/phase-4.md)
5. [Phase 5 — Demo Readiness](docs/phase-5.md)

For the presentation sequence, use [the demo script](docs/demo-script.md).
