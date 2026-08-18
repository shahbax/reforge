# Reforge — Production Launch Checklist (Honest)

_Read this before flipping it live. It separates what's DONE from what still needs YOUR accounts/keys to actually earn money._

## ✅ Done and verified
- Full app: marketing site (SEO-optimized) → real Supabase auth (ES256) → dashboard → analyze → Viral DNA → concepts → original script → Originality Guard → export.
- Beginner UX: onboarding, "try an example", plain-language tooltips, "how to make this video", monetization note.
- SEO: metadata/OpenGraph/Twitter, robots.txt, sitemap.xml, JSON-LD, noindex on app routes.
- Backend: FastAPI, credit tracking, usage/cost accounting, SSRF-guarded ingestion, 17 tests passing.
- On GitHub: https://github.com/shahbax/reforge

## ⚠️ 3 things stand between "works" and "earning" — do these before charging anyone

### 1. Turn on the REAL AI engine (currently mock)
Right now analysis/script output is deterministic **fixtures**, not real AI. To make it real:
```
cd backend && ./.venv/Scripts/python -m pip install -r requirements-optional.txt   # anthropic, yt-dlp, openai
```
In `backend/.env`:
```
AI_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-...        # from console.anthropic.com
```
Restart backend. Ingestion (yt-dlp) will fetch real videos/captions; Claude will produce real Viral DNA + scripts. **Cost control ships next: prompt caching + duration caps (see go-live-plan.md §2).**

### 2. Persistent database (currently in-memory — data resets on every restart)
This is the #1 blocker to a real launch: with the in-memory store, **every backend restart/redeploy wipes all users and projects.** Needed: a `PostgresStore` (interface already exists in `store.py`) against your Supabase Postgres, with the schema in `database.md`. **Recommend I build this next — it's ~1 focused session and I can run the migrations on your Supabase project directly.**

### 3. Billing (Stripe) — required to actually collect money
Credits are tracked but there's no checkout yet. Needs Stripe products/prices + webhook to grant credits on payment. I can build this behind the existing credit system once you add Stripe keys.

## Supabase settings to set (5 minutes, in your dashboard)
- **Auth → Providers → Email:** for easy signups, turn **off** "Confirm email" (or configure SMTP for confirmation emails).
- **Auth → URL Configuration:** set **Site URL** and **Redirect URLs** to your production domain (and `http://localhost:3000` for dev).
- **(Optional) Google provider:** add Google OAuth client ID/secret to enable the "Continue with Google" button.

## Deployment (when 1–3 are ready)
**Frontend → Vercel:**
- Import the repo, root = `frontend`.
- Env: `NEXT_PUBLIC_API_BASE=https://<your-backend>/api/v1`, `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `NEXT_PUBLIC_SITE_URL=https://<your-domain>`.

**Backend → Render / Railway / Fly / VPS:**
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Env: `AI_PROVIDER=claude`, `ANTHROPIC_API_KEY`, `SUPABASE_URL`, `SUPABASE_JWT_SECRET`, `DATABASE_URL` (Postgres), `CORS_ORIGINS=https://<your-domain>`, `ENVIRONMENT=production`.
- `pip install -r requirements.txt -r requirements-optional.txt`.

**Domain + DNS:** point your domain at Vercel; set `NEXT_PUBLIC_SITE_URL` and `CORS_ORIGINS` accordingly.

## Post-deploy (day 1)
- Submit `https://<domain>/sitemap.xml` to **Google Search Console** + **Bing Webmaster**.
- Wire **PostHog** (funnel) + **Sentry** (errors).
- Smoke-test the full flow on production with a real account; confirm credits debit and a real Claude analysis returns.

## Honest status line
**Production-quality code, SEO, and UX are finished.** To *earn*, you still need: real AI key (5 min), **Postgres persistence (build next)**, Stripe (build next), and deploy. Do not take paying customers until persistence + billing are in — otherwise a redeploy wipes their data and you can't collect payment.
