# Go-Live, Cost & Monetization Plan — Reforge

_Compiled 2026-08-18. Concrete numbers are estimates for planning; re-verify provider pricing before committing spend._

The goal: launch fast, keep fixed cost **near zero until there's revenue**, keep the system **fast and fully SEO-optimized**, and have a clear path from launch → first dollars → durable margin.

---

## 1. Architecture for launch (minimum cost, fast, scalable)

Chosen to minimize fixed cost and moving parts while staying fast and SEO-friendly.

| Layer | Choice | Why | Cost at launch |
|---|---|---|---|
| Frontend/marketing | **Next.js on Vercel** | Edge CDN = fast globally; SSG/SSR = excellent SEO; zero-config deploys | **$0** (Hobby) → $20/mo Pro later |
| Backend API | **FastAPI on a small VPS** (Hetzner CPX21) or Render | Cheapest reliable always-on host; runs the pipeline + background jobs | **~$7/mo** |
| Auth + DB + Storage | **Supabase** (free tier) | Auth (50k MAU), Postgres (500MB), storage — one service, less glue | **$0** → $25/mo Pro at scale |
| Queue/cache | **Upstash Redis** (free) — deferred | Not needed day 1 (in-process jobs); add for scale/long videos | **$0** |
| Transcription | **captions-first (yt-dlp)** → Whisper fallback | Most YouTube videos have captions = **$0** transcription | ~$0 avg |
| LLM | **Claude** (Haiku for cheap stages, Sonnet for DNA/script) | Quality where it matters, cheap everywhere else | variable (see §2) |
| Domain | e.g. reforge.app / getreforge.com | — | **~$1/mo** ($12/yr) |
| Email | **Resend** (free 3k/mo) | Auth + transactional | **$0** |
| Analytics | **PostHog** or **Plausible** (free tiers) | Funnel + product analytics | **$0** |
| Errors | **Sentry** (free tier) | Catch prod errors | **$0** |
| Payments | **Stripe** | Subscriptions + usage | 2.9% + 30¢ per charge |

**Fixed monthly cost at launch: ≈ $8–$15/mo** (essentially VPS + domain).
**At early traction (first paying users): ≈ $50–$70/mo** (add Supabase Pro + Vercel Pro).

> Alternative "everything managed" path: backend on Render/Railway (~$7–20), same Supabase/Vercel. Slightly more $, less ops. Recommended if you'd rather not touch a VPS.

---

## 2. The number that decides the business: cost per analysis

One full run = **Analysis job** (content analysis → Viral DNA → concepts) + **Script job** (research → script → originality). Originality Guard runs **locally = $0**.

Estimated tokens & cost per stage (transcript ~1.5–3k tokens reused across stages):

| Stage | Model | ~in / out tokens | Cost |
|---|---|---|---|
| Content analysis | Haiku | 2.5k / 0.5k | $0.004 |
| **Viral DNA** | Sonnet | 3k / 1.5k | $0.032 |
| **Concepts (5–10)** | Sonnet | 2k / 2k | $0.036 |
| Research brief | Haiku | 1k / 0.7k | $0.004 |
| **Script** | Sonnet | 3k / 2k | $0.039 |
| Production package | Haiku | 1.5k / 0.5k | $0.003 |
| Originality Guard | local | — | $0.000 |
| Transcription | captions/Whisper | — | ~$0–0.06 |

- **Naive cost per full run ≈ $0.12–$0.20.**
- **With Claude prompt caching** on the transcript (reused in 6 stages, cached input ≈ 10% price) **≈ $0.08–$0.12.**

**Plan on ~$0.20 conservative / ~$0.10 optimized per full analysis+script.** This is the single most important lever — the cost-control mechanisms below protect it.

### Cost-control levers (already partly built)
1. **Prompt caching** of the transcript across stages — biggest single saving. _(next to implement)_
2. **Haiku for cheap stages**, Sonnet only for DNA/concepts/script — already wired via `tier`.
3. **Captions-first transcription** — $0 for most videos — already the ingestion path.
4. **Transcript reuse / video-id dedupe** — already built (idempotent `POST /analyses`).
5. **Credit ceilings + per-IP rate limits** on free tier — credits built; add IP limits.
6. **Max duration caps** on free/low tiers to bound transcription + token cost.

---

## 3. Unit economics & pricing

Per §2, assume **$0.20/run conservative** (improves to ~$0.10 with caching).

| Plan | Price | Included | Est. LLM cost @ $0.20 | Gross margin |
|---|---|---|---|---|
| **Free** | $0 | 2 runs/mo | ~$0.40 | acquisition (loss leader, capped) |
| **Creator** | **$19/mo** | ~30 runs | ~$6 | **~68%** ($13) → ~84% cached |
| **Pro** | **$39/mo** | ~120 runs | ~$24 | ~38% ($15) → **~69% cached** |
| **Agency** | **$99/mo** | ~400 runs + bulk/channel | ~$80 | thin naive → healthy cached; gated on caching |

Notes:
- Margins are **healthy on Creator immediately** and become healthy on Pro/Agency **once prompt caching ships** — so caching is a launch-blocker for the higher tiers.
- **Credits map to real cost**, so a heavy user can't blow up margin — overflow is sold as top-up packs.
- **Annual plans** (2 months free) improve cashflow and retention.
- Undercuts the credible competitor (Subscribr $59, YouTube-only) while owning the Originality Guard nobody else has.

---

## 4. How we earn (revenue model)

1. **Subscriptions (primary)** — Free → Creator → Pro → Agency, monthly + annual, via Stripe.
2. **Credit top-ups** — pay-as-you-go packs for users who exceed plan credits.
3. **Annual prepay** — discounted, improves cashflow.
4. **Later expansion:** API access (Agency/devs), team seats, channel-level bulk analysis, white-label for agencies.

Target early metric: **first paying customers within the launch month**; north-star = weekly completed analyses per active user + % of scripts exported.

---

## 5. SEO strategy (a primary growth channel, not an afterthought)

This product is unusually SEO-able — lean into it hard.

**Technical foundation (do first, ~1–2 days):**
- SSG landing + marketing pages (Next.js) for speed + crawlability.
- `metadata` API on every page, `sitemap.xml`, `robots.txt`, canonical URLs.
- OpenGraph/Twitter cards + **JSON-LD structured data** (SoftwareApplication, FAQ, Article).
- Core Web Vitals green (Vercel edge + our light UI already helps).

**Content & programmatic SEO (the flywheel):**
- **A free tool as a lead magnet** (e.g. a public "Hook Analyzer" or "Viral Title Analyzer") — competitors (HookLab) prove this drives traffic; it also funnels into signup.
- **Programmatic pages** targeting long-tail intent: "YouTube script generator for {niche}", "{niche} video ideas", "how to make faceless {niche} videos".
- **Keyword content** from our competitor research: _youtube script generator, faceless youtube automation, viral video analyzer, video to script, reused content demonetization_ (the last ties to our Originality Guard — a unique PR/SEO angle).
- **Shareable public report pages** (opt-in, indexable) → organic backlinks; private analyses stay `noindex`.

**Off-site / launch traffic:** Product Hunt launch, Reddit (r/NewTubers, r/youtubers, faceless-channel subs), YouTube-automation Discords, X/Twitter build-in-public.

---

## 6. The launch path (sequenced, ~4 weeks to paid launch)

**Phase 0 — Auth & persistence (this week)**
- Supabase Auth (email + Google) — login/signup UI + real JWT verification (backend already supports it).
- PostgresStore behind the existing `Store` interface (schema in `database.md`); replace in-memory.
- Deploy: Vercel (frontend) + VPS/Render (backend) + Supabase — staging live.

**Phase 1 — Real engine + cost guards (week 1–2)**
- Wire real Claude provider + captions-first/Whisper ingestion (abstractions ready).
- **Prompt caching** on transcript; enforce credit ceilings, per-IP rate limits, duration caps.
- Sentry + PostHog wired.

**Phase 2 — SEO foundation (week 2–3)**
- SSG landing, metadata/sitemap/robots/JSON-LD, 1 free tool, 5–10 seed content/programmatic pages.

**Phase 3 — Billing & polish (week 3–4)**
- Stripe live (subscriptions + top-ups), paywall behind credits, onboarding, empty/loading/error states.

**Phase 4 — Launch (week 4)**
- Soft launch to communities → Product Hunt → iterate on activation and funnel.

**Ongoing:** content/SEO flywheel, funnel optimization, then channel-level analysis (V2 expansion).

---

## 7. Biggest risks & mitigations
- **LLM cost blowout** → caching + Haiku-first + captions-first + credit ceilings (see §2).
- **Ingestion/ToS reliability** (downloading) → captions-first, clear ToS, no permanent video storage.
- **Perceived as a "copy" tool** → positioning + Originality Guard + persistent "not legal advice" disclaimer.
- **Factual hallucination** → fact/claim/opinion separation for factual niches (built into the research stage).
- **Free-tier abuse** → per-IP limits, tight free caps, email verification.

---

## 8. TL;DR
- **Fixed cost to launch: ~$10/mo**, rising to ~$50–70/mo at first traction.
- **Variable cost: ~$0.10–0.20 per full analysis+script** — margins healthy on Creator now, on all tiers once prompt caching ships.
- **Earn** via Free→Creator($19)→Pro($39)→Agency($99) subscriptions + credit top-ups.
- **Grow** via aggressive SEO (free tool + programmatic pages + the Originality-Guard angle) plus community/PH launch.
- **Path:** Auth+DB → real engine+cost guards → SEO → Stripe → launch, ~4 weeks.
