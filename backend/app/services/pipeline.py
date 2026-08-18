"""Pipeline orchestrator.

Wires the specialized stages together and manages job state transitions.
Split into two jobs at concept selection (see docs/mvp-spec.md):

  run_analysis_job(): DOWNLOADING -> TRANSCRIBING -> ANALYZING
                      -> GENERATING_CONCEPTS -> AWAITING_CONCEPT_SELECTION
  run_script_job():   RESEARCHING -> GENERATING_SCRIPT -> CHECKING_ORIGINALITY
                      -> COMPLETED

Each generative call is validated against a Pydantic schema by the provider.
Usage/token accounting hooks are called per stage.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from app.schemas import (
    ConceptSet,
    ContentAnalysis,
    JobStatus,
    OriginalityReport,
    ProductionPackage,
    ResearchBrief,
    Script,
    ScriptControls,
    SourceVideoMeta,
    Transcript,
    ViralDNA,
)
from app.services.ai import prompts
from app.services.ai.provider import BaseProvider, get_provider
from app.services.ingestion import youtube
from app.services.originality import guard

log = logging.getLogger("reforge.pipeline")

StatusCallback = Callable[[JobStatus, Optional[str]], None]


@dataclass
class AnalysisResult:
    meta: SourceVideoMeta
    transcript: Transcript
    analysis: ContentAnalysis
    dna: ViralDNA
    concepts: ConceptSet
    stage_costs: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class ScriptResult:
    research: ResearchBrief
    script: Script
    originality: OriginalityReport
    package: ProductionPackage
    stage_costs: list[dict[str, Any]] = field(default_factory=list)


def _noop(status: JobStatus, detail: Optional[str] = None) -> None:
    log.info("stage=%s detail=%s", status.value, detail)


# --------------------------------------------------------------------------- #
# Analysis job
# --------------------------------------------------------------------------- #
def run_analysis_job(
    url: str,
    *,
    niche_hint: str = "",
    audience_hint: str = "",
    on_status: StatusCallback = _noop,
    provider: BaseProvider | None = None,
) -> AnalysisResult:
    provider = provider or get_provider()

    on_status(JobStatus.DOWNLOADING, "fetching video metadata")
    meta, transcript = youtube.fetch(url)

    on_status(JobStatus.TRANSCRIBING, "extracting transcript")
    if transcript is None:
        # captions-first transcription would run here; dev fallback provides text
        from app.services.transcription.transcriber import transcribe

        transcript = transcribe(meta)

    on_status(JobStatus.ANALYZING, "analyzing content")
    analysis = provider.complete(
        system=prompts.CONTENT_ANALYST,
        user=_analysis_prompt(meta, transcript),
        schema=ContentAnalysis,
        tier="cheap",
    )
    dna = provider.complete(
        system=prompts.VIRAL_DNA,
        user=_dna_prompt(analysis, transcript),
        schema=ViralDNA,
        tier="strong",
    )

    on_status(JobStatus.GENERATING_CONCEPTS, "generating original concepts")
    concepts = provider.complete(
        system=prompts.CONCEPT_GENERATOR,
        user=_concepts_prompt(dna, niche_hint or analysis.niche, audience_hint),
        schema=ConceptSet,
        tier="strong",
    )

    on_status(JobStatus.AWAITING_CONCEPT_SELECTION, "ready for concept selection")
    return AnalysisResult(meta=meta, transcript=transcript, analysis=analysis, dna=dna, concepts=concepts)


# --------------------------------------------------------------------------- #
# Script job
# --------------------------------------------------------------------------- #
def run_script_job(
    *,
    dna: ViralDNA,
    concept_index: int,
    concepts: ConceptSet,
    controls: ScriptControls,
    source_transcript: Transcript,
    on_status: StatusCallback = _noop,
    provider: BaseProvider | None = None,
) -> ScriptResult:
    provider = provider or get_provider()
    concept = concepts.concepts[concept_index]

    on_status(JobStatus.RESEARCHING, "researching the selected angle")
    research = provider.complete(
        system=prompts.RESEARCH_AGENT,
        user=_research_prompt(concept, controls),
        schema=ResearchBrief,
        tier="cheap",
    )

    on_status(JobStatus.GENERATING_SCRIPT, "writing original script")
    script = provider.complete(
        system=prompts.SCRIPT_WRITER,
        user=_script_prompt(dna, concept, research, controls),
        schema=Script,
        tier="strong",
    )
    script.word_count = len(script.full_text.split())

    on_status(JobStatus.CHECKING_ORIGINALITY, "running originality analysis")
    embeddings = provider.embed([source_transcript.full_text, script.full_text])
    originality = guard.build_report(
        source=source_transcript.full_text,
        generated=script.full_text,
        source_embedding=embeddings[0],
        generated_embedding=embeddings[1],
    )

    package = provider.complete(
        system=prompts.FINALIZER,
        user=f"Final script:\n{script.full_text}\n\nPlatform: {controls.platform.value}",
        schema=ProductionPackage,
        tier="cheap",
    )

    on_status(JobStatus.COMPLETED, "done")
    return ScriptResult(research=research, script=script, originality=originality, package=package)


def rewrite_flagged(
    *,
    script: Script,
    originality: OriginalityReport,
    source_transcript: Transcript,
    provider: BaseProvider | None = None,
) -> tuple[Script, OriginalityReport]:
    """Rewrite flagged passages toward higher originality, then re-score."""
    provider = provider or get_provider()
    if not originality.flagged_sections:
        return script, originality
    flagged = "\n".join(f"- {f.script_excerpt}" for f in originality.flagged_sections)
    revised = provider.complete(
        system=prompts.ORIGINALITY_REWRITER,
        user=f"Script:\n{script.full_text}\n\nRewrite these flagged passages:\n{flagged}",
        schema=Script,
        tier="strong",
    )
    revised.word_count = len(revised.full_text.split())
    embeddings = provider.embed([source_transcript.full_text, revised.full_text])
    report = guard.build_report(
        source=source_transcript.full_text,
        generated=revised.full_text,
        source_embedding=embeddings[0],
        generated_embedding=embeddings[1],
    )
    return revised, report


# --------------------------------------------------------------------------- #
# Prompt builders (kept small; the heavy instruction lives in system prompts)
# --------------------------------------------------------------------------- #
def _analysis_prompt(meta: SourceVideoMeta, transcript: Transcript) -> str:
    return (
        f"Video title: {meta.title}\nPlatform: {meta.platform.value}\n"
        f"Transcript:\n{transcript.full_text}"
    )


def _dna_prompt(analysis: ContentAnalysis, transcript: Transcript) -> str:
    return (
        f"Content analysis: niche={analysis.niche}, topic={analysis.topic}, "
        f"structure={analysis.structure}\nTranscript:\n{transcript.full_text}"
    )


def _concepts_prompt(dna: ViralDNA, niche: str, audience: str) -> str:
    return (
        f"Viral DNA (mechanics only): {dna.model_dump_json()}\n"
        f"Target niche: {niche}\nTarget audience: {audience or dna.target_audience}\n"
        "Generate at least 5 divergent original concepts."
    )


def _research_prompt(concept, controls: ScriptControls) -> str:
    return (
        f"Concept: {concept.model_dump_json()}\nNiche: {controls.niche}\n"
        f"Research level: {controls.research_level}"
    )


def _script_prompt(dna, concept, research, controls: ScriptControls) -> str:
    return (
        f"Viral DNA mechanics: {dna.model_dump_json()}\n"
        f"Chosen concept: {concept.model_dump_json()}\n"
        f"Research brief: {research.model_dump_json()}\n"
        f"Controls: platform={controls.platform.value}, tone={controls.tone}, "
        f"language={controls.language}, style={controls.storytelling_style}, "
        f"cta={controls.cta_style}, target_words={controls.target_word_count}"
    )
