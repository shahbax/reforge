"""End-to-end pipeline test with the mock provider (no keys, no network)."""
from app.schemas import ScriptControls
from app.services.ai.provider import MockProvider
from app.services.pipeline import run_analysis_job, run_script_job

URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


def test_analysis_produces_dna_and_concepts():
    provider = MockProvider()
    result = run_analysis_job(URL, provider=provider)

    assert result.meta.external_id == "dQw4w9WgXcQ"
    assert result.dna.niche
    assert 0 <= result.dna.hook.strength <= 100
    assert len(result.concepts.concepts) >= 5
    for concept in result.concepts.concepts:
        assert concept.title and concept.hook and concept.how_it_differs_from_source
    # provider recorded per-call usage
    assert provider.usage and all(u["input_tokens"] > 0 for u in provider.usage)


def test_script_job_respects_controls_and_scores_originality():
    provider = MockProvider()
    analysis = run_analysis_job(URL, provider=provider)

    controls = ScriptControls(duration_seconds=180, tone="curious")
    script_provider = MockProvider()
    out = run_script_job(
        dna=analysis.dna,
        concept_index=0,
        concepts=analysis.concepts,
        controls=controls,
        source_transcript=analysis.transcript,
        provider=script_provider,
    )

    assert out.script.title
    assert out.script.word_count > 0
    assert out.script.sections
    assert 0 <= out.originality.originality_score <= 100
    assert out.originality.disclaimer  # never empty
