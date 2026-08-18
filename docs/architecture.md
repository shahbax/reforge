# Architecture — Reforge

## 1. Stack decision & rationale

| Layer | Choice | Why (vs alternatives) |
|---|---|---|
| Frontend | **Next.js 14 (App Router) + TypeScript + Tailwind + shadcn/ui** | Matches brief and the team's existing stack (PropFlow/Relicsol). Vercel deploy. |
| Backend API | **Python + FastAPI** | Video/AI tooling (yt-dlp, ffmpeg, faster-whisper, tokenizers) is Python-native. Async, typed, Pydantic schemas fit the "structured JSON between stages" requirement. |
| Async processing | **Redis + RQ workers** | Long video/AI jobs must not block requests. RQ is simplest robust option; can swap to Celery/arq later. Job state persisted in Postgres. |
| DB | **PostgreSQL (Supabase)** | Relational schema, RLS for multi-tenant isolation. Supabase gives us Auth + Postgres + Storage in one, consistent with team's other projects. |
| Auth | **Supabase Auth** | Fastest reliable path; frontend SDK + backend JWT verification. (Clerk/Auth.js were considered; Supabase wins on DB+Storage integration.) |
| Storage | **Supabase Storage (S3-compatible)** | Uploaded MP4s + generated exports. Don't persist raw video long-term. |
| AI | **Claude API primary** via a provider abstraction (OpenAI pluggable) | Brief prefers Claude/OpenAI. Abstraction lets us route cheap vs. strong models per stage. |
| Transcription | **Captions-first (yt-dlp) → faster-whisper fallback**, provider-abstracted (Deepgram pluggable) | Cheapest correct path: reuse existing captions; only transcribe audio when needed. |
| Video | **yt-dlp + ffmpeg** | Metadata, captions, audio extraction. Used within ToS/legal limits. |
| Payments | **Stripe** (flagged off until pricing validated) | Credits tracked from day one; paywall behind a feature flag. |

Deviation from brief: we use **Supabase** for Auth+DB+Storage rather than raw Postgres + a separate auth provider, because it collapses three services into one and matches the team's proven stack. The AI/backend design is otherwise as specified.

## 2. High-level topology

```
             ┌────────────────────────┐
  Browser ──▶│  Next.js (Vercel)      │  UI, auth session, calls API
             │  App Router + shadcn   │
             └───────────┬────────────┘
                         │ HTTPS (JWT)
                         ▼
             ┌────────────────────────┐        ┌───────────────┐
             │  FastAPI (Render/Railway)│──────▶│ Redis (queue) │
             │  REST API, auth verify,  │       └──────┬────────┘
             │  credit checks, job mgmt │              │ RQ
             └───────┬─────────┬────────┘              ▼
                     │         │              ┌────────────────────┐
                     │         │              │  Worker process(es) │
                     ▼         ▼              │  pipeline stages    │
             ┌──────────┐ ┌──────────┐        └─────────┬──────────┘
             │ Postgres │ │ Supabase │◀─────────────────┘
             │ (Supabase)│ │ Storage │   read/write rows, artifacts
             └──────────┘ └──────────┘
                     ▲
                     │ Claude API / Whisper / yt-dlp (from workers)
```

The API stays thin: validate → enqueue → return job. Workers do the heavy pipeline and write results + token/cost accounting back to Postgres. The frontend polls job status (SSE/polling) and renders stages.

## 3. Module layout (monorepo)

```
reforge/
  frontend/                  # Next.js app
    app/                     # routes: /, /login, /dashboard, /analysis/[id]
    components/              # shadcn-based UI
    lib/                     # api client, supabase client, types
  backend/
    app/
      main.py                # FastAPI entrypoint
      config.py              # env-driven settings (pydantic-settings)
      db.py                  # SQLAlchemy engine/session
      models.py             # ORM models (mirrors database.md)
      schemas.py            # Pydantic API + pipeline schemas
      security.py          # JWT verify, rate limit, SSRF guard
      api/                  # routers: auth, projects, analyses, scripts, usage
      services/
        ingestion/          # yt-dlp metadata + captions + audio, URL validation
        transcription/      # provider abstraction (captions | whisper | deepgram)
        ai/                 # LLM provider abstraction (claude | openai), prompts
        analysis/           # Viral DNA stage
        concepts/           # concept generation stage
        research/           # research agent (stub-real: web/fact separation)
        script/             # script writer stage
        originality/        # originality guard (metrics + rewrite)
        credits/            # usage accounting
      workers/
        queue.py            # RQ setup
        pipeline.py         # stage orchestration + state transitions
    tests/
  docs/
  docker-compose.yml         # local: postgres, redis (Supabase optional local)
```

Separation of concerns: each `services/*` module has a typed input/output schema and is independently testable. The pipeline orchestrator wires them; no giant monolithic file, no single mega-prompt.

## 4. Cross-cutting concerns
- **Config:** all secrets via env (`pydantic-settings`); never shipped to frontend.
- **Errors & retries:** external calls (LLM, yt-dlp, whisper) wrapped with tenacity retries + typed exceptions; failures set job `FAILED` with a user-safe reason.
- **Logging:** structured logging with a `job_id` correlation id per pipeline run.
- **Validation:** every LLM response validated against a Pydantic schema; on invalid JSON, one repair retry, then fail the stage cleanly.
- **Security:** SSRF guard on URL ingestion (host allowlist for known platforms, block private IP ranges), upload size/type limits, per-user rate limits, RLS in Postgres, JWT verification on every API call.
- **Cost:** model routing per stage; token usage recorded to `usage_records`; per-user credit ceiling enforced before enqueue.

## 5. Extensibility for channel analysis (V2)
`source_videos` are decoupled from `projects`; a future `channels` table + a batch job that fans out per-video analyses reuses the exact same pipeline stages. Outlier detection becomes a new pre-stage feeding the same concept/script/originality flow. Nothing in the MVP schema blocks this.
