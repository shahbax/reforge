# Database — Reforge

PostgreSQL (Supabase). UUID primary keys, `created_at`/`updated_at` on all tables, RLS so a user sees only their own rows. Raw video is not persisted long-term (audio deleted after transcription; only transcript/meta kept).

## Entities

### users
Managed by Supabase Auth (`auth.users`). A `public.profiles` row mirrors app data.
- `id (uuid, = auth.users.id)`, `email`, `display_name`, `plan (free|creator|pro|agency)`, `credits_remaining int`, `credits_reset_at`, timestamps.

### projects
A unit of work started from one source video.
- `id uuid`, `user_id uuid fk`, `title`, `status` (enum: queued…completed/failed), `stage` (current pipeline stage), `error_reason nullable`, `source_video_id fk`, `selected_concept_id nullable fk`, timestamps.
- index: `(user_id, created_at desc)`.

### source_videos  (decoupled from projects → enables channel analysis later)
- `id uuid`, `platform (youtube|tiktok|instagram|upload)`, `external_id` (e.g. YouTube video id), `url`, `title`, `channel_name`, `duration_seconds`, `published_at`, `view_count`, `metadata jsonb`, timestamps.
- unique: `(platform, external_id)` → transcript/analysis reuse.

### video_transcripts
- `id uuid`, `source_video_id fk`, `language`, `source (captions|whisper|deepgram)`, `segments jsonb` (`[{start,end,text}]`), `full_text text`, `token_count`, timestamps.
- unique: `(source_video_id, language)`.

### video_analysis  (Content Analyst output)
- `id uuid`, `source_video_id fk`, `niche`, `topic`, `structure jsonb`, `factual_claims jsonb`, `raw jsonb`, timestamps.

### viral_dna
- `id uuid`, `source_video_id fk`, `dna jsonb` (validated ViralDNA schema), `model`, `version`, timestamps.
- one-per-source-video (regeneratable; keep latest + version).

### content_concepts
- `id uuid`, `project_id fk`, `viral_dna_id fk`, `concepts jsonb` (array), `model`, timestamps.

### research_results
- `id uuid`, `project_id fk`, `concept_index int`, `brief jsonb` (verified_facts/claims/opinions/sources), `model`, timestamps.

### scripts
- `id uuid`, `project_id fk`, `concept_index int`, `controls jsonb`, `script jsonb` (sections), `full_text text`, `word_count`, `model`, `version int`, timestamps.

### originality_reports
- `id uuid`, `script_id fk`, `originality_score int`, `phrase_overlap`, `distinctive_phrase_overlap`, `semantic_similarity`, `structural_similarity` (numeric + band), `flagged_sections jsonb`, `disclaimer text`, timestamps.

### usage_records  (cost/credit accounting)
- `id uuid`, `user_id fk`, `project_id fk nullable`, `stage`, `model`, `prompt_tokens`, `completion_tokens`, `cost_estimate numeric`, `credits_charged int`, `created_at`.
- index: `(user_id, created_at)`.

### subscriptions  (Stripe; inert until billing enabled)
- `id uuid`, `user_id fk`, `stripe_customer_id`, `stripe_subscription_id`, `plan`, `status`, `current_period_end`, timestamps.

## Notes
- All child rows carry `user_id` (or join to it) for RLS policies: `user_id = auth.uid()`.
- `jsonb` used for evolving AI outputs; the *shape* is enforced in the app layer via Pydantic before insert, so schema drift doesn't corrupt reads.
- Indexes added on all FKs and on `(user_id, created_at)` list paths.
- Migrations live in `backend/migrations/` (SQL) and are also expressible as Supabase migrations.
