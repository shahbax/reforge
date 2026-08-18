# AI Pipeline — Reforge

Design principle: **no single mega-prompt.** The pipeline is a sequence of specialized stages, each with a typed JSON contract validated against a Pydantic schema. Cheap models do extraction/summarization; strong models do reasoning-heavy stages (DNA, script, originality).

## Stages

```
INGESTION → TRANSCRIPT → (VISUAL — deferred) → CONTENT ANALYST → VIRAL DNA
   → CONCEPT GENERATOR → [user selects] → RESEARCH → SCRIPT WRITER → ORIGINALITY GUARD → FINALIZER
```

| Stage | Input | Output schema | Model tier | Notes |
|---|---|---|---|---|
| Ingestion | URL/upload | `SourceVideoMeta` | none (yt-dlp) | metadata, captions availability, duration, audio path |
| Transcript | audio/captions | `Transcript` (segments+text) | cheap/none | captions reused if present; else Whisper |
| Content Analyst | transcript + meta | `ContentAnalysis` | cheap–mid | niche, topic, structure segments, factual claims list |
| **Viral DNA** | ContentAnalysis + transcript | `ViralDNA` | **strong** | the differentiator; explainable mechanics |
| **Concept Generator** | ViralDNA + user niche/audience | `ConceptSet` (≥5) | strong | divergent angles; explicit `how_it_differs` |
| Research | selected concept | `ResearchBrief` | mid (+web later) | fact/claim/opinion separation; citations retained internally |
| **Script Writer** | concept + DNA + research + controls | `Script` | **strong** | mechanics-reuse, not wording-reuse |
| **Originality Guard** | source transcript + script | `OriginalityReport` | mixed (embeddings + strong) | metrics + flagged sections + rewrite |
| Finalizer | Script + reports | `ProductionPackage` | cheap | titles, thumbnail prompts, description, hashtags, export |

## Viral DNA schema (core fields)
`niche, topic, subtopic, target_audience, content_archetype, hook.{type,strength,curiosity_mechanism}, emotional_progression[], narrative_structure[], story_arc, information_density, pacing, pattern_interrupts[], open_loops[], payoff_points[], escalation_points[], cta_strategy, title_strategy, thumbnail_strategy, visual_patterns[], retention_hypotheses[], why_it_worked[], reusable_principles[]`.

Every field is populated from the transcript/analysis — the extractor is instructed to describe **mechanics**, never to quote distinctive wording.

## Concept schema
Each concept: `title, premise, unique_angle, hook, target_audience, emotional_journey, why_it_could_work, how_it_differs_from_source, suggested_structure[]`.

## Script controls (user-set)
`platform, niche, target_audience, language, tone, duration_seconds → target_word_count, storytelling_style, angle, research_level, cta_style`.

## Originality Guard
Produces `OriginalityReport`:
- `originality_score` (0–100)
- `phrase_overlap`, `distinctive_phrase_overlap`, `semantic_similarity`, `structural_similarity` (each LOW/MODERATE/HIGH + numeric)
- `flagged_sections[]` — {script_excerpt, source_reference, reason, severity, char_range}
- `disclaimer` — always: *"Originality analysis is an AI-based similarity assessment and is not legal advice or a guarantee against copyright claims."*

Method (MVP): normalized n-gram overlap (phrase), rarity-weighted n-gram overlap (distinctive phrase), embedding cosine similarity (semantic), section-sequence alignment (structural). An LLM pass explains flags and, on "Rewrite," regenerates flagged sections toward lower similarity while preserving meaning.

## Anti-copy prompting (enforced across generative stages)
System prompts instruct: reuse **ideas, structure, hook type, pacing, emotional beats**; never reuse **distinctive phrases, dialogue, unique sequences, or creative wording**. The Script Writer receives the DNA (mechanics) and the *concept*, **not** the raw source wording, to reduce leakage. Originality Guard is the backstop.

## Research agent (factual rigor)
Separates `verified_facts` / `claims` / `opinions` / `speculation`; for factual niches (history, science, finance, true crime, news) the script writer may only assert items marked verified, and hedges claims. Citations retained internally now; surfaced to users in a later phase.

## Cost model (indicative, per full run)
| Stage | Tokens (rough) | Model | Notes |
|---|---|---|---|
| Content Analyst | 3–8k in / 1k out | cheap | scales with transcript length (chunked) |
| Viral DNA | 4–10k in / 2k out | strong | |
| Concepts | 3k in / 3k out | strong | |
| Research | 2k in / 2k out | mid | web calls later |
| Script | 4k in / 3–6k out | strong | scales with duration |
| Originality | embeddings + 3k in / 1k out | mixed | |

Controls: transcript reuse (dedupe by video id), chunking + map-reduce summarization for long videos, per-stage token caps, credit ceiling per user, model tier routing. Every stage writes `{prompt_tokens, completion_tokens, model, cost_estimate}` to `usage_records` for real margin calculation.

## Provider abstraction
`ai/provider.py` exposes `complete(messages, schema, tier)` and `embed(texts)`. Implementations: `ClaudeProvider` (default), `OpenAIProvider` (pluggable). A `MockProvider` returns schema-valid fixtures so the pipeline and UI are fully testable without API keys (dev fallback only; production requires real keys).
