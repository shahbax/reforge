"""Typed contracts for the Reforge pipeline.

Every LLM stage must return JSON that validates against one of these models.
These are the enforced boundaries between stages (see docs/ai-pipeline.md).
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, HttpUrl


# --------------------------------------------------------------------------- #
# Job / pipeline state
# --------------------------------------------------------------------------- #
class JobStatus(str, Enum):
    QUEUED = "QUEUED"
    DOWNLOADING = "DOWNLOADING"
    TRANSCRIBING = "TRANSCRIBING"
    ANALYZING = "ANALYZING"
    GENERATING_CONCEPTS = "GENERATING_CONCEPTS"
    AWAITING_CONCEPT_SELECTION = "AWAITING_CONCEPT_SELECTION"
    RESEARCHING = "RESEARCHING"
    GENERATING_SCRIPT = "GENERATING_SCRIPT"
    CHECKING_ORIGINALITY = "CHECKING_ORIGINALITY"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Platform(str, Enum):
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    UPLOAD = "upload"


# --------------------------------------------------------------------------- #
# Ingestion / transcript
# --------------------------------------------------------------------------- #
class SourceVideoMeta(BaseModel):
    platform: Platform
    external_id: str
    url: str
    title: str = ""
    channel_name: str = ""
    duration_seconds: int = 0
    published_at: Optional[str] = None
    view_count: Optional[int] = None
    has_captions: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class TranscriptSegment(BaseModel):
    start: float
    end: float
    text: str


class Transcript(BaseModel):
    language: str = "en"
    source: Literal["captions", "whisper", "deepgram", "mock"] = "captions"
    segments: list[TranscriptSegment] = Field(default_factory=list)
    full_text: str
    token_count: int = 0


# --------------------------------------------------------------------------- #
# Content analysis + Viral DNA
# --------------------------------------------------------------------------- #
class FactualClaim(BaseModel):
    claim: str
    kind: Literal["verified_fact", "claim", "opinion", "speculation"] = "claim"


class ContentAnalysis(BaseModel):
    niche: str
    topic: str
    subtopic: str = ""
    target_audience: str = ""
    structure: list[str] = Field(default_factory=list)
    factual_claims: list[FactualClaim] = Field(default_factory=list)


class Hook(BaseModel):
    type: str
    strength: int = Field(ge=0, le=100)
    curiosity_mechanism: str = ""


class ViralDNA(BaseModel):
    niche: str
    topic: str
    subtopic: str = ""
    target_audience: str = ""
    content_archetype: str = ""
    hook: Hook
    emotional_progression: list[str] = Field(default_factory=list)
    narrative_structure: list[str] = Field(default_factory=list)
    story_arc: str = ""
    information_density: str = ""
    pacing: str = ""
    pattern_interrupts: list[str] = Field(default_factory=list)
    open_loops: list[str] = Field(default_factory=list)
    payoff_points: list[str] = Field(default_factory=list)
    escalation_points: list[str] = Field(default_factory=list)
    cta_strategy: str = ""
    title_strategy: str = ""
    thumbnail_strategy: str = ""
    visual_patterns: list[str] = Field(default_factory=list)
    retention_hypotheses: list[str] = Field(default_factory=list)
    why_it_worked: list[str] = Field(default_factory=list)
    reusable_principles: list[str] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# Concepts
# --------------------------------------------------------------------------- #
class Concept(BaseModel):
    title: str
    premise: str
    unique_angle: str
    hook: str
    target_audience: str
    emotional_journey: str
    why_it_could_work: str
    how_it_differs_from_source: str
    suggested_structure: list[str] = Field(default_factory=list)


class ConceptSet(BaseModel):
    concepts: list[Concept] = Field(min_length=1)


# --------------------------------------------------------------------------- #
# Research + script
# --------------------------------------------------------------------------- #
class ResearchBrief(BaseModel):
    verified_facts: list[str] = Field(default_factory=list)
    claims: list[str] = Field(default_factory=list)
    opinions: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)


class ScriptControls(BaseModel):
    platform: Platform = Platform.YOUTUBE
    niche: str = ""
    target_audience: str = ""
    language: str = "en"
    tone: str = "engaging"
    duration_seconds: int = 300
    storytelling_style: str = "narrative"
    angle: str = ""
    research_level: Literal["light", "standard", "deep"] = "standard"
    cta_style: str = "subscribe"

    @property
    def target_word_count(self) -> int:
        # ~150 spoken words per minute
        return max(80, int(self.duration_seconds / 60 * 150))


class ScriptSection(BaseModel):
    label: str
    content: str


class Script(BaseModel):
    title: str
    sections: list[ScriptSection]
    full_text: str
    word_count: int = 0


# --------------------------------------------------------------------------- #
# Originality
# --------------------------------------------------------------------------- #
Band = Literal["LOW", "MODERATE", "HIGH"]


class Metric(BaseModel):
    value: float = Field(ge=0.0, le=1.0)
    band: Band


class FlaggedSection(BaseModel):
    script_excerpt: str
    source_reference: str
    reason: str
    severity: Literal["low", "medium", "high"]
    char_start: int
    char_end: int


DISCLAIMER = (
    "Originality analysis is an AI-based similarity assessment and is not legal "
    "advice or a guarantee against copyright claims."
)


class OriginalityReport(BaseModel):
    originality_score: int = Field(ge=0, le=100)
    phrase_overlap: Metric
    distinctive_phrase_overlap: Metric
    semantic_similarity: Metric
    structural_similarity: Metric
    flagged_sections: list[FlaggedSection] = Field(default_factory=list)
    disclaimer: str = DISCLAIMER


# --------------------------------------------------------------------------- #
# API surface
# --------------------------------------------------------------------------- #
class AnalyzeRequest(BaseModel):
    url: HttpUrl


class ProductionPackage(BaseModel):
    titles: list[str] = Field(default_factory=list)
    thumbnail_prompts: list[str] = Field(default_factory=list)
    description: str = ""
    hashtags: list[str] = Field(default_factory=list)
