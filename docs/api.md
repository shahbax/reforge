# API — Reforge (FastAPI)

Base: `/api/v1`. Auth: `Authorization: Bearer <supabase-jwt>` on all routes except health. All responses JSON. Errors: `{ "error": { "code", "message" } }`.

## Auth / profile
- `GET  /me` → profile + plan + credits.
- `POST /me/credits/refill` (admin/dev) → reset credits.

## Analyses (Analysis job: URL → DNA → concepts)
- `POST /analyses` — body `{ url }` (or multipart upload). Validates + SSRF-guards, dedupes by video id, checks credits, enqueues. → `{ project_id, status }`.
- `GET  /analyses/{project_id}` → `{ status, stage, error_reason?, source_video, viral_dna?, concepts? }`.
- `GET  /analyses/{project_id}/events` (SSE) → stage transitions for live progress.
- `GET  /projects?limit=&cursor=` → paginated project history.
- `DELETE /projects/{id}`.

## Scripts (Script job: concept → research → script → originality)
- `POST /projects/{id}/script` — body `{ concept_index, controls }` (platform, tone, duration_seconds, language, cta_style, storytelling_style, research_level). Checks credits, enqueues. → `{ script_job: queued }`.
- `GET  /projects/{id}/script` → `{ status, stage, script?, originality_report? }`.
- `POST /scripts/{script_id}/rewrite` — body `{ target: flagged|all }` → new script version with improved originality.
- `GET  /projects/{id}/export?format=md|txt` → downloadable export (production package).

## Usage
- `GET /usage?from=&to=` → aggregated tokens/cost/credits by stage + remaining credits.

## Health
- `GET /health` → `{ ok: true }` (no auth).

## Conventions
- Idempotency: `POST /analyses` with same URL within a window returns the existing in-flight/complete project (transcript reuse).
- Rate limits: per-user token bucket on generative POSTs.
- Every generative POST debits credits atomically before enqueue; refunded on stage FAIL.
- Job status polling via `GET` or live via SSE `/events`.
