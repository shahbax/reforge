# MVP Specification — Reforge

## Goal
Ship the core loop end-to-end for **YouTube URLs**: **Analyze → Viral DNA → Concepts → Original Script → Originality Guard**, with auth, project history, exports, and credit tracking. Everything must actually work — no fake buttons, no hardcoded AI responses.

## In scope (MVP)
1. Landing page communicating the value in seconds.
2. Auth (Supabase Auth: email + OAuth).
3. Dashboard: Projects, New Analysis, Usage, Settings.
4. **New Analysis** — paste a YouTube URL.
5. Async video processing with visible job stages.
6. Transcript extraction (captions-first, Whisper fallback).
7. AI content analysis → **Viral DNA** report.
8. **5+ original content concepts** (divergent angles).
9. User selects a concept.
10. **Original script generation** (platform/tone/duration/language controls).
11. **Originality analysis** (source vs generated: phrase/distinctive-phrase/semantic/structural + score + flagged sections + rewrite action).
12. Save projects; project history.
13. Export script (Markdown / plain text / copy).
14. Credit/usage tracking per project and per user.
15. Clean, responsive SaaS UI with polished loading states.

## Nice-to-have (only if cheap to add)
- MP4 upload support (provider abstraction already allows it).
- TikTok / Instagram URL support (yt-dlp already supports; gated on reliability).

## Explicitly NOT in MVP
AI video/voice gen, auto-publish, avatars, team mgmt, enterprise billing, mobile app, channel analysis (architecture-ready, not built), Stripe live billing (credits tracked; paywall stubbed behind a flag until pricing validated).

## Job state machine
`QUEUED → DOWNLOADING → TRANSCRIBING → ANALYZING → GENERATING_CONCEPTS → (user selects) → RESEARCHING → GENERATING_SCRIPT → CHECKING_ORIGINALITY → COMPLETED` (+ `FAILED` from any state, with reason).

Note: concept selection splits the pipeline into two async jobs — **Analysis job** (through concepts) and **Script job** (research → script → originality) — so the user reviews DNA + concepts before spending credits on a script.

## Acceptance criteria (per feature)
- **Ingestion:** rejects non-URL / unsupported host; SSRF-safe; enforces max duration; dedupes by video id (transcript reuse).
- **Viral DNA:** returns schema-valid JSON with all required fields; renders as a structured report, not a wall of text.
- **Concepts:** ≥5 concepts, each with title/premise/angle/hook/audience/emotional journey/why-it-works/how-it-differs/structure; schema-validated.
- **Script:** respects user controls (platform, tone, duration→word count, language, CTA); returns sectioned script.
- **Originality Guard:** returns 0–100 score + four sub-metrics + flagged sections with offsets; "Rewrite" produces a lower-similarity revision; disclaimer always shown.
- **Credits:** every generative step debits credits; usage visible; free-tier limit enforced server-side.
- **Security:** all AI/keys server-side; RLS so users only see their own projects; upload/url validation; rate limiting.

## Cost controls (MVP)
Transcript reuse by video id; chunked transcripts; cheap model for extraction/summarization, stronger model for DNA/script/originality; per-user credit ceiling; token accounting persisted per stage.
