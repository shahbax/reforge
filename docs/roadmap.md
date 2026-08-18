# Roadmap — Reforge

## Phase 0 — Foundation (this build)
- Repo scaffold, docs, config, provider abstraction, schemas, DB models, local dev (docker-compose: postgres+redis), MockProvider so the pipeline runs without keys.

## MVP milestones
1. **Project foundation** — monorepo, config, schemas, health, CI-ready. ← in progress
2. **Auth + database** — Supabase Auth verify, profiles, migrations, RLS, credits.
3. **YouTube ingestion** — yt-dlp metadata + captions, SSRF guard, dedupe.
4. **Transcript pipeline** — captions-first, Whisper fallback, chunking.
5. **Viral DNA analysis** — Content Analyst + DNA stages, schema-validated.
6. **Concept generation** — ≥5 divergent concepts.
7. **Script generation** — controls → sectioned script.
8. **Originality Guard** — metrics + flagged sections + rewrite.
9. **Dashboard / project history** — full UI, live stages, export.
10. **Polish / testing / deploy** — tests, types, lint, Vercel + Render/Railway.

After each milestone: run tests, fix errors, check types/lint, update docs.

## Post-MVP (V2+)
- MP4 upload + TikTok/Instagram at reliability parity.
- Visual analysis agent (keyframes → visual patterns).
- Research agent with live web + surfaced citations.
- **Channel analysis**: paste channel → outliers → gaps → opportunities → scripts (architecture already supports it).
- Stripe live billing once unit economics validated.
- Team seats, API access, automation (n8n/webhooks).

## Biggest risks (tracked)
- **Technical:** transcript reliability across platforms; long-video cost; LLM JSON validity; yt-dlp/ToS fragility.
- **Legal/product:** never promise copyright safety; originality guard is assistive, not a guarantee; platform scraping limits.
- **Economics:** per-analysis cost vs. price; controlled via model routing, caching, credit ceilings.
