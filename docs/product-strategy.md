# Product Strategy — Reforge

> Working name: **Reforge** ("Reverse-engineer virality. Forge something original.")
> Name alternatives shortlisted: Reforge, ViralDNA, ContentDNA, DecodeAI, Overtone, Throughline, Prooflight. Not final — chosen to avoid bikeshedding during build.

## 1. One-line positioning
**Viral Content Intelligence + Original Content Generation** — understand *why* a video worked at the mechanics level, then create something genuinely original from those principles, with a similarity audit that keeps you on the right side of derivative.

Explicitly **not** "copy a viral video 90% and dodge copyright." That framing is both a legal risk and a crowded, low-trust corner of the market.

## 2. Target customer
- **Primary:** faceless-channel creators and content-automation operators (often running multiple channels) who need a repeatable, defensible ideation→script pipeline.
- **Secondary:** solo long-form/Shorts creators, short-form marketers, and small agencies producing content for clients.
- **Tertiary (later):** teams needing channel-level gap analysis and bulk generation.

## 3. Jobs to be done
1. "I found a video that's clearly working — help me understand *why* without watching it 5 times."
2. "Give me original directions I can actually make, not a paraphrase of the original."
3. "Write me a research-grounded script that won't hallucinate facts in my niche."
4. "Reassure me (and give me evidence) that what I'm publishing isn't a derivative copy."

## 4. Differentiation (ranked)
1. **Originality Guard** — source-vs-generated similarity audit with rewrite. *No competitor has this.* Directly serves the legal/ethical positioning and creator anxiety about reused-content policies.
2. **Viral DNA** — a deep, structured, *explainable* mechanics report (hook type, curiosity mechanism, emotional progression, open loops, escalation, retention hypotheses) — beyond the shallow hook/structure/CTA breakdowns competitors ship.
3. **Divergent concept generation** — 5–10 genuinely different angles engineered to *reuse mechanics, not wording*, with an explicit "how it differs from source" field.
4. **Research-grounded scripts** with fact/claim/opinion separation for factual niches (history, science, finance, true crime, news).
5. **Transparent economics** — visible credits and per-project cost, honest about model usage.

## 5. Guardrails / principles
- Never promise copyright safety. Originality analysis is an AI similarity assessment, **not legal advice** — this disclaimer ships in-product wherever a score appears.
- The system actively steers away from near-verbatim output: mechanics are reusable (ideas, structures, hooks, pacing); distinctive wording/dialogue/sequences are not.
- Separate ideas/facts/topics/structure (reusable) from original wording/expression/creative passages (protectable).

## 6. Pricing hypothesis (to validate)
| Plan | Price | Analyses / credits | Notes |
|---|---|---|---|
| Free | $0 | 2 analyses / mo, watermark on export | Acquisition; full pipeline, limited volume |
| Creator | ~$19/mo | ~30 analyses, all niches | Undercuts Subscribr's $59 entry |
| Pro | ~$39–$49/mo | ~120 analyses, deeper research, priority | Core revenue tier |
| Agency | ~$99+/mo | Bulk + channel analysis (later), seats | Expansion revenue |

Credits map to real pipeline cost (see `ai-pipeline.md` cost model). Pricing is **not final** until unit economics from real usage are measured.

## 7. Success metrics (early)
- Activation: % of new users who complete one full analysis→script within 24h.
- Value: % of generated scripts exported/used; median Originality Score.
- Retention: weekly analyses per active user; W4 retention.
- Economics: cost per analysis, gross margin per plan.

## 8. What we deliberately defer
AI video/voice generation, auto-publishing, avatars, team management, enterprise billing, mobile app, many AI providers. Architecture must not preclude channel-level analysis (a clear V2 expansion).
