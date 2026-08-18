# Reforge

**Viral Content Intelligence + Original Content Generation.**

Reforge reverse-engineers *why* a video worked — at the mechanics level — and helps
creators produce something **genuinely original** from those principles, with a
built-in similarity audit that keeps the output on the right side of derivative.

> Reforge is **not** a "copy a viral video and dodge copyright" tool. It separates
> reusable mechanics (ideas, structure, hooks, pacing, emotional progression) from
> protectable expression (distinctive wording, dialogue, sequences) and actively
> steers generation away from near-verbatim output.

The core loop:

```
Viral video URL → Understand → Extract "Viral DNA" → Generate original concepts
→ Research → Write original script → Originality Guard → Production package
```

---

## Why Reforge

Competitor research (see [`docs/competitor-research.md`](docs/competitor-research.md))
found the market crowded with shallow "hook / structure / CTA" script generators and
a low-trust corner selling copyright-dodging. Our differentiation:

1. **Originality Guard** — a source-vs-generated similarity audit (phrase, distinctive-phrase,
   semantic, structural) with a 0–100 score, flagged passages, and one-click rewrite.
   *No competitor ships this.*
2. **Viral DNA** — a deep, structured, **explainable** mechanics report, not a wall of text.
3. **Divergent concept generation** — 5–10 genuinely different angles engineered to reuse
   mechanics, not wording, each with an explicit "how it differs from source".
4. **Research-grounded scripts** with fact / claim / opinion separation for factual niches.
5. **Transparent economics** — visible per-project token cost and credits.

Full strategy: [`docs/product-strategy.md`](docs/product-strategy.md).

---

## Status

| Area | State |
|---|---|
| Product docs (research, strategy, MVP, architecture, AI pipeline, DB, API, roadmap) | ✅ `docs/` |
| Backend services (ingestion, transcription, AI provider, Viral DNA, concepts, script, Originality Guard, pipeline) | ✅ `backend/app/services/` |
| **Backend API** (FastAPI: analyses, scripts, projects, usage, auth, credits, jobs) | ✅ `backend/app/` |
| Test suite (pipeline e2e, originality, ingestion/SSRF, full API flow) | ✅ 17 passing |
| **Frontend** (Next.js 16 + Tailwind v4): landing, dashboard, analysis workspace, Viral DNA report, concept picker, script controls, Originality Guard UI, export | ✅ `frontend/` (typechecks + builds clean) |
| Auth (Supabase login UI) | ⏳ next — backend dev-auth used for now |
| Postgres/Supabase persistence, real ingestion (yt-dlp), Claude provider | 🔌 abstractions ready, wire keys to enable |

The whole backend runs **keyless** in development: a mock AI provider returns
schema-valid fixtures and ingestion falls back to a dev stub, so the full pipeline
and API work end-to-end with no API keys.

---

## Quickstart (backend)

Requires Python 3.11+ (developed on 3.14).

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate   |   Unix: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # optional — defaults run in mock mode
pytest                        # 17 tests, no keys needed
uvicorn app.main:app --reload # http://localhost:8000  (docs at /docs)
```

Try the loop with the API running (dev auth attributes you to a dev user):

```bash
# 1. Start an analysis (returns a project_id)
curl -s -X POST localhost:8000/api/v1/analyses \
  -H 'content-type: application/json' \
  -d '{"url":"https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'

# 2. Read the Viral DNA + concepts
curl -s localhost:8000/api/v1/analyses/<project_id>

# 3. Generate a script from a concept
curl -s -X POST localhost:8000/api/v1/projects/<project_id>/script \
  -H 'content-type: application/json' \
  -d '{"concept_index":0,"controls":{"platform":"youtube","duration_seconds":180}}'

# 4. Read the script + originality report, then export
curl -s localhost:8000/api/v1/projects/<project_id>/script
curl -s "localhost:8000/api/v1/projects/<project_id>/export?format=md"
```

## Quickstart (frontend)

Requires Node 20+ (developed on 24). With the backend running on `:8000`:

```bash
cd frontend
npm install
npm run dev          # http://localhost:3000
```

The landing page is at `/`, the app at `/dashboard`. In dev the frontend talks to the
backend's dev-auth mode (no login yet), so you can run the full loop immediately.
Override the API base with `NEXT_PUBLIC_API_BASE` in `frontend/.env.local`.

### Going live (real integrations)

```bash
pip install -r requirements-optional.txt   # anthropic, yt-dlp, openai
```

Then in `.env`: set `AI_PROVIDER=claude` + `ANTHROPIC_API_KEY`, add `SUPABASE_JWT_SECRET`
to enforce real auth, and `DATABASE_URL` once the Postgres store lands (M2). Every
integration is behind an abstraction (`services/ai/provider.py`, `services/ingestion/`,
`store.py`) — no code changes needed, just configuration.

---

## Architecture

```
backend/
  app/
    main.py            FastAPI app: routers, CORS, error handling, lifespan
    config.py          env-driven settings (never hardcode secrets)
    schemas.py         typed contracts between every pipeline stage
    store.py           Store interface + InMemoryStore (Postgres store = M2)
    auth.py            Supabase JWT verify + dev fallback
    jobs.py            background job manager (thread pool / inline)
    deps.py            FastAPI dependencies (store, jobs, current user, ownership)
    routers/           me, analyses, projects, scripts, usage, health
    services/
      ingestion/       URL validation + SSRF guard + yt-dlp (dev stub fallback)
      transcription/   captions-first, Whisper fallback
      ai/              provider (Claude / mock), prompts, fixtures, cost model
      originality/     deterministic similarity guard (offline-testable)
      pipeline.py      two-phase orchestrator (analysis → concepts → script)
```

Design notes live in [`docs/architecture.md`](docs/architecture.md) and
[`docs/ai-pipeline.md`](docs/ai-pipeline.md).

**Tech stack:** FastAPI + Pydantic (backend) · Next.js/TypeScript/Tailwind/shadcn (frontend, next) ·
Claude API (primary LLM) · yt-dlp + Whisper (ingestion/transcription) · Supabase Auth ·
Postgres · Redis (queue, later) · Stripe (billing, later).

---

## Legal / product principle

Reforge never promises copyright safety. The Originality Guard is an **AI-based
similarity assessment, not legal advice or a guarantee against copyright claims** —
that disclaimer ships in-product wherever a score appears.

---

## Docs

- [Competitor research](docs/competitor-research.md)
- [Product strategy](docs/product-strategy.md)
- [MVP spec](docs/mvp-spec.md)
- [Architecture](docs/architecture.md)
- [AI pipeline](docs/ai-pipeline.md)
- [Database](docs/database.md)
- [API](docs/api.md)
- [Roadmap](docs/roadmap.md)
