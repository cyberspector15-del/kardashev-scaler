# Phase 1 — Project Foundation

## What was scaffolded

- FastAPI backend with local-development CORS and a `GET /health` endpoint.
- React + Vite + TypeScript frontend with React Router routes for Home and Dashboard.
- Tailwind CSS and a central monochrome design-token system.
- Reusable, scalable SVG `Logo` component based on the supplied visual reference.

## Folder structure

```text
kardashev-scaler/
├── backend/
│   ├── .env.example
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── models/
│       ├── routers/
│       └── services/
├── frontend/
│   ├── src/
│   │   ├── components/Logo.tsx
│   │   ├── pages/
│   │   └── theme.ts
│   ├── tailwind.config.ts
│   └── package.json
└── docs/
    └── phase-1.md
```

## Locked design tokens

- Background: `#000000`
- Primary text: `#f5f5f5`
- Glow: `#ffffff`
- Radius: `0px` globally; all UI corners are sharp.
- Shadows: disabled except the white-only `glow` token.
- Headline font: Dune Rise with League Spartan / Arial Black geometric fallbacks.
- Body font: DM Sans.

The same tokens are defined in `frontend/src/theme.ts` and Tailwind configuration.

## Run locally

Backend (from `backend`):

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The health check is available at `http://127.0.0.1:8000/health` and returns `{"status":"ok"}`.

Frontend (from `frontend`):

```bash
npm install
npm run dev
```

Vite serves the frontend locally (normally at `http://localhost:5173`).
