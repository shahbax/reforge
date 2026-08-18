"""Schema-valid fixtures for MockProvider.

These let the full pipeline and UI run with no API keys (development fallback).
They are intentionally generic and original so the originality guard scores them
realistically. Production uses a real provider instead.
"""
from __future__ import annotations

import re


def fixture_for(schema_name: str, user_prompt: str) -> dict:
    data = _FIXTURES.get(schema_name, {})
    # Personalize demo output to the chosen concept so regenerating from a
    # different concept visibly changes the script (real providers do this
    # naturally; the mock otherwise returns an identical fixture every time).
    if schema_name in ("Script", "ProductionPackage"):
        return _personalize(schema_name, data, user_prompt)
    return data


def _extract(field: str, prompt: str) -> str | None:
    m = re.search(r'"' + field + r'"\s*:\s*"([^"]{3,160})"', prompt)
    return m.group(1) if m else None


def _personalize(schema_name: str, data: dict, prompt: str) -> dict:
    title = _extract("title", prompt)  # the chosen concept's title
    hook = _extract("hook", prompt)    # the chosen concept's hook line
    if not title:
        return data

    if schema_name == "Script":
        data = {**data, "title": title}
        sections = [dict(s) for s in data.get("sections", [])]
        if sections and hook:
            sections[0] = {**sections[0], "content": hook}
            data["sections"] = sections
            data["full_text"] = " ".join(s["content"] for s in sections)
        return data

    if schema_name == "ProductionPackage":
        titles = [title] + [t for t in data.get("titles", []) if t != title]
        return {**data, "titles": titles[:3]}

    return data


_FIXTURES: dict[str, dict] = {
    "ContentAnalysis": {
        "niche": "science explainer",
        "topic": "an unexpected phenomenon explained simply",
        "subtopic": "cause-and-effect walkthrough",
        "target_audience": "curious general audience, 18-34",
        "structure": [
            "cold-open question",
            "context",
            "first surprising fact",
            "mechanism explained",
            "counterintuitive twist",
            "payoff",
            "call to action",
        ],
        "factual_claims": [
            {"claim": "the effect is widely observed", "kind": "claim"},
            {"claim": "it was formally described decades ago", "kind": "verified_fact"},
        ],
    },
    "ViralDNA": {
        "niche": "science explainer",
        "topic": "an unexpected phenomenon explained simply",
        "subtopic": "cause-and-effect walkthrough",
        "target_audience": "curious general audience, 18-34",
        "content_archetype": "curiosity-driven explainer",
        "hook": {
            "type": "contradiction / unanswered question",
            "strength": 82,
            "curiosity_mechanism": "poses a question that violates the viewer's assumption",
        },
        "emotional_progression": ["curiosity", "confusion", "concern", "surprise", "revelation"],
        "narrative_structure": [
            "hook", "context", "first mystery", "evidence", "contradiction",
            "escalation", "major reveal", "resolution", "cta",
        ],
        "story_arc": "question -> investigation -> reveal -> reframing",
        "information_density": "moderate-high, one idea per beat",
        "pacing": "fast open, steady middle, quick payoff",
        "pattern_interrupts": ["visual cut on each new claim", "rhetorical question every ~30s"],
        "open_loops": ["the real reason is withheld until the reveal"],
        "payoff_points": ["the reveal recontextualizes the opening question"],
        "escalation_points": ["stakes raised by a second, larger example"],
        "cta_strategy": "soft ask tied to curiosity ('which surprised you?')",
        "title_strategy": "curiosity gap + concrete noun",
        "thumbnail_strategy": "single subject + a question mark cue",
        "visual_patterns": ["tight cuts", "on-screen text emphasis"],
        "retention_hypotheses": [
            "open loop delays payoff to hold viewers",
            "frequent pattern interrupts reset attention",
        ],
        "why_it_worked": [
            "hook creates an information gap",
            "each beat pays a small curiosity debt and opens a new one",
        ],
        "reusable_principles": [
            "open with a violated assumption",
            "withhold the core explanation behind an open loop",
            "escalate with a bigger example before the reveal",
        ],
    },
    "ConceptSet": {
        "concepts": [
            {
                "title": "The everyday habit that quietly reshapes your week",
                "premise": "A small routine most people ignore compounds into large effects.",
                "unique_angle": "frame it as an invisible compounding system, not a life hack",
                "hook": "You repeat this 40 times a week and never notice what it does.",
                "target_audience": "productivity-curious general audience",
                "emotional_journey": "skepticism -> recognition -> surprise -> motivation",
                "why_it_could_work": "uses the source's open-loop reveal on a fresh, relatable topic",
                "how_it_differs_from_source": "different niche, different subject, only the curiosity mechanics are reused",
                "suggested_structure": ["hook", "relatable setup", "hidden mechanism", "bigger example", "reveal", "cta"],
            },
            {
                "title": "Why the 'boring' choice usually wins",
                "premise": "Counterintuitively, unremarkable options outperform flashy ones over time.",
                "unique_angle": "contrarian reframing backed by simple reasoning",
                "hook": "The most exciting option is usually the wrong one. Here's why.",
                "target_audience": "decision-makers, students",
                "emotional_journey": "curiosity -> doubt -> agreement",
                "why_it_could_work": "contradiction hook mirrors the source's proven mechanic",
                "how_it_differs_from_source": "new domain and argument; shares only the contradiction hook type",
                "suggested_structure": ["contradiction hook", "context", "evidence", "twist", "payoff", "cta"],
            },
            {
                "title": "The mistake hidden inside good advice",
                "premise": "Popular advice contains a flaw people rarely question.",
                "unique_angle": "expose the flaw, then offer a cleaner rule",
                "hook": "This advice is everywhere. It's also quietly wrong.",
                "target_audience": "self-improvement audience",
                "emotional_journey": "recognition -> concern -> relief",
                "why_it_could_work": "open-loop + reveal structure adapted to a myth-busting angle",
                "how_it_differs_from_source": "myth-busting framing on unrelated subject matter",
                "suggested_structure": ["hook", "the common advice", "the hidden flaw", "the better rule", "cta"],
            },
            {
                "title": "A tiny number that predicts a big outcome",
                "premise": "One overlooked metric forecasts results better than obvious ones.",
                "unique_angle": "single-number reveal with a satisfying payoff",
                "hook": "Ignore the big numbers. This small one tells the real story.",
                "target_audience": "data-curious general audience",
                "emotional_journey": "curiosity -> surprise -> clarity",
                "why_it_could_work": "escalation-then-reveal pacing reused on a data topic",
                "how_it_differs_from_source": "quantitative angle, distinct topic and script",
                "suggested_structure": ["hook", "why obvious metrics mislead", "the small metric", "proof", "reveal", "cta"],
            },
            {
                "title": "The thing that changed when nobody was watching",
                "premise": "A quiet shift had outsized consequences later.",
                "unique_angle": "before/after story with a delayed payoff",
                "hook": "Nothing looked different. Everything was.",
                "target_audience": "story-driven viewers",
                "emotional_journey": "intrigue -> tension -> revelation",
                "why_it_could_work": "delayed-payoff open loop mirrors the source mechanic",
                "how_it_differs_from_source": "narrative story format on a new subject",
                "suggested_structure": ["hook", "the calm before", "the quiet change", "the consequence", "reveal", "cta"],
            },
        ]
    },
    "ResearchBrief": {
        "verified_facts": [
            "compounding effects are well documented in behavioral research",
        ],
        "claims": [
            "small routines can meaningfully affect weekly outcomes",
            "people systematically underestimate cumulative effects",
        ],
        "opinions": ["the 'boring' option is underrated"],
        "open_questions": ["how large is the effect for an average person?"],
        "sources": [],
    },
    "Script": {
        "title": "The everyday habit that quietly reshapes your week",
        "sections": [
            {"label": "Hook", "content": "You do this roughly forty times a week, and you have never once stopped to ask what it is actually doing to you."},
            {"label": "Setup", "content": "It feels far too small to matter. That is exactly why it slips past your attention, week after week, without a second thought."},
            {"label": "Mechanism", "content": "Each repetition nudges the next decision in the same direction. Alone, a nudge is nothing. Stacked, they quietly steer the whole week."},
            {"label": "Escalation", "content": "Now imagine that same nudge running for a year. The tiny thing you dismissed becomes the current your choices drift along."},
            {"label": "Reveal", "content": "The habit was never the point. The point is that you are already running dozens of these invisible systems, and you get to choose which ones."},
            {"label": "CTA", "content": "So here is the honest question: which of your small repeated habits is quietly steering your week? Tell me the first one that comes to mind."},
        ],
        "full_text": (
            "You do this roughly forty times a week, and you have never once stopped to ask what it is "
            "actually doing to you. It feels far too small to matter. That is exactly why it slips past "
            "your attention, week after week, without a second thought. Each repetition nudges the next "
            "decision in the same direction. Alone, a nudge is nothing. Stacked, they quietly steer the "
            "whole week. Now imagine that same nudge running for a year. The tiny thing you dismissed "
            "becomes the current your choices drift along. The habit was never the point. The point is "
            "that you are already running dozens of these invisible systems, and you get to choose which "
            "ones. So here is the honest question: which of your small repeated habits is quietly steering "
            "your week? Tell me the first one that comes to mind."
        ),
        "word_count": 0,
    },
    "ProductionPackage": {
        "titles": [
            "The everyday habit that quietly reshapes your week",
            "You do this 40 times a week (and never notice)",
            "The tiny habit steering your whole week",
        ],
        "thumbnail_prompts": [
            "single everyday object with a subtle question mark, high contrast",
            "split before/after with one small highlighted detail",
        ],
        "description": "A short exploration of how small repeated habits compound into outsized effects on your week.",
        "hashtags": ["#habits", "#productivity", "#selfimprovement", "#mindset"],
    },
}
