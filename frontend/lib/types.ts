// Mirrors backend/app/schemas.py — keep in sync with the API contracts.

export type JobStatus =
  | "QUEUED"
  | "DOWNLOADING"
  | "TRANSCRIBING"
  | "ANALYZING"
  | "GENERATING_CONCEPTS"
  | "AWAITING_CONCEPT_SELECTION"
  | "RESEARCHING"
  | "GENERATING_SCRIPT"
  | "CHECKING_ORIGINALITY"
  | "COMPLETED"
  | "FAILED";

export type Platform = "youtube" | "tiktok" | "instagram" | "upload";
export type Band = "LOW" | "MODERATE" | "HIGH";

export interface SourceVideoMeta {
  platform: Platform;
  external_id: string;
  url: string;
  title: string;
  channel_name: string;
  duration_seconds: number;
  view_count: number | null;
  has_captions: boolean;
}

export interface Hook {
  type: string;
  strength: number;
  curiosity_mechanism: string;
}

export interface ViralDNA {
  niche: string;
  topic: string;
  subtopic: string;
  target_audience: string;
  content_archetype: string;
  hook: Hook;
  emotional_progression: string[];
  narrative_structure: string[];
  story_arc: string;
  information_density: string;
  pacing: string;
  pattern_interrupts: string[];
  open_loops: string[];
  payoff_points: string[];
  escalation_points: string[];
  cta_strategy: string;
  title_strategy: string;
  thumbnail_strategy: string;
  visual_patterns: string[];
  retention_hypotheses: string[];
  why_it_worked: string[];
  reusable_principles: string[];
}

export interface Concept {
  title: string;
  premise: string;
  unique_angle: string;
  hook: string;
  target_audience: string;
  emotional_journey: string;
  why_it_could_work: string;
  how_it_differs_from_source: string;
  suggested_structure: string[];
}

export interface ConceptSet {
  concepts: Concept[];
}

export interface AnalysisView {
  project_id: string;
  status: JobStatus;
  stage: string;
  error_reason: string | null;
  source_video: SourceVideoMeta | null;
  viral_dna: ViralDNA | null;
  concepts: ConceptSet | null;
  created_at: string;
  updated_at: string;
}

export interface ScriptControls {
  platform: Platform;
  niche: string;
  target_audience: string;
  language: string;
  tone: string;
  duration_seconds: number;
  storytelling_style: string;
  angle: string;
  research_level: "light" | "standard" | "deep";
  cta_style: string;
}

export interface ScriptSection {
  label: string;
  content: string;
}

export interface Script {
  title: string;
  sections: ScriptSection[];
  full_text: string;
  word_count: number;
}

export interface Metric {
  value: number;
  band: Band;
}

export interface FlaggedSection {
  script_excerpt: string;
  source_reference: string;
  reason: string;
  severity: "low" | "medium" | "high";
  char_start: number;
  char_end: number;
}

export interface OriginalityReport {
  originality_score: number;
  phrase_overlap: Metric;
  distinctive_phrase_overlap: Metric;
  semantic_similarity: Metric;
  structural_similarity: Metric;
  flagged_sections: FlaggedSection[];
  disclaimer: string;
}

export interface ResearchBrief {
  verified_facts: string[];
  claims: string[];
  opinions: string[];
  open_questions: string[];
  sources: string[];
}

export interface ProductionPackage {
  titles: string[];
  thumbnail_prompts: string[];
  description: string;
  hashtags: string[];
}

export interface ScriptView {
  project_id: string;
  script_id: string | null;
  status: JobStatus | null;
  stage: string;
  error_reason: string | null;
  concept_index: number | null;
  controls: ScriptControls | null;
  research: ResearchBrief | null;
  script: Script | null;
  originality_report: OriginalityReport | null;
  production_package: ProductionPackage | null;
}

export interface ProjectSummary {
  project_id: string;
  url: string;
  platform: Platform;
  title: string;
  status: JobStatus;
  script_status: JobStatus | null;
  originality_score: number | null;
  created_at: string;
  updated_at: string;
}

export interface Me {
  id: string;
  email: string;
  plan: string;
  credits: number;
}

export interface Usage {
  remaining_credits: number;
  plan: string;
  totals: { cost_usd: number; input_tokens: number; output_tokens: number };
  by_stage: Record<
    string,
    { input_tokens: number; output_tokens: number; cost_usd: number; calls: number }
  >;
}
