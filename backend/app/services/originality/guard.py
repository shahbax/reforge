"""Originality Guard — source-vs-generated similarity audit.

This is a real, deterministic algorithm (no LLM required for the core metrics):

  * phrase_overlap            — Jaccard over shared word n-grams (n=3..5)
  * distinctive_phrase_overlap— rarity-weighted overlap (rare shared phrases count
                                more; boilerplate counts little)
  * semantic_similarity       — cosine over provided embeddings
  * structural_similarity     — order-aware alignment of the two texts' beats
  * flagged_sections          — the actual overlapping passages, with offsets

An optional LLM pass can explain/rewrite flagged sections, but the scores stand
on their own and are fully unit-testable offline.

Nothing here is a legal guarantee — the report always carries the disclaimer.
"""
from __future__ import annotations

import math
import re
from collections import Counter

from app.schemas import (
    Band,
    FlaggedSection,
    Metric,
    OriginalityReport,
)

_WORD = re.compile(r"[a-z0-9']+")


def _words(text: str) -> list[str]:
    return _WORD.findall(text.lower())


def _ngrams(words: list[str], n: int) -> list[tuple[str, ...]]:
    return [tuple(words[i : i + n]) for i in range(len(words) - n + 1)]


def _band(value: float) -> Band:
    if value < 0.15:
        return "LOW"
    if value < 0.40:
        return "MODERATE"
    return "HIGH"


def _metric(value: float) -> Metric:
    value = max(0.0, min(1.0, value))
    return Metric(value=round(value, 4), band=_band(value))


# --------------------------------------------------------------------------- #
# Core metrics
# --------------------------------------------------------------------------- #
def phrase_overlap(source: str, generated: str, ns: tuple[int, ...] = (3, 4, 5)) -> float:
    """Jaccard similarity over the union of word n-grams for several n."""
    sw, gw = _words(source), _words(generated)
    scores: list[float] = []
    for n in ns:
        s = set(_ngrams(sw, n))
        g = set(_ngrams(gw, n))
        if not s or not g:
            continue
        inter = len(s & g)
        union = len(s | g)
        scores.append(inter / union if union else 0.0)
    return sum(scores) / len(scores) if scores else 0.0


def distinctive_phrase_overlap(source: str, generated: str, n: int = 4) -> float:
    """Rarity-weighted shared-phrase overlap.

    Shared n-grams are weighted by inverse document frequency across the two
    documents' phrase distributions, so distinctive (rare) shared phrases —
    the ones that actually signal copying — dominate over common filler.
    """
    sg = _ngrams(_words(source), n)
    gg = _ngrams(_words(generated), n)
    if not sg or not gg:
        return 0.0
    s_counts, g_counts = Counter(sg), Counter(gg)
    shared = set(s_counts) & set(g_counts)
    if not shared:
        return 0.0
    total = Counter(sg) + Counter(gg)
    weighted_shared = 0.0
    for gram in shared:
        # rarer overall => higher weight
        weight = 1.0 / math.log2(total[gram] + 2)
        weighted_shared += weight
    denom = sum(1.0 / math.log2(total[g] + 2) for g in set(g_counts))
    return weighted_shared / denom if denom else 0.0


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return max(0.0, dot / (na * nb))


def structural_similarity(source: str, generated: str, segments: int = 6) -> float:
    """Order-aware similarity of the two texts' 'beats'.

    Each text is split into equal segments; we compare the per-segment word-set
    Jaccard along the diagonal. High only when similar content appears in the
    same relative order (i.e. the structure was copied, not just vocabulary).
    """
    def chunks(text: str) -> list[set[str]]:
        w = _words(text)
        if len(w) < segments:
            return [set(w)]
        size = math.ceil(len(w) / segments)
        return [set(w[i : i + size]) for i in range(0, len(w), size)][:segments]

    sc, gc = chunks(source), chunks(generated)
    pairs = min(len(sc), len(gc))
    if not pairs:
        return 0.0
    total = 0.0
    for i in range(pairs):
        a, b = sc[i], gc[i]
        union = len(a | b)
        total += (len(a & b) / union) if union else 0.0
    return total / pairs


# --------------------------------------------------------------------------- #
# Flagged sections
# --------------------------------------------------------------------------- #
def find_flagged_sections(
    source: str, generated: str, n: int = 5, max_flags: int = 12
) -> list[FlaggedSection]:
    """Locate the longest verbatim/near-verbatim shared spans in `generated`."""
    src_grams = set(_ngrams(_words(source), n))
    gen_words = _words(generated)
    gen_grams = _ngrams(gen_words, n)

    # mark generated n-gram positions that also appear in the source
    hits = [i for i, gram in enumerate(gen_grams) if gram in src_grams]
    if not hits:
        return []

    # merge consecutive hit positions into spans
    spans: list[tuple[int, int]] = []
    start = prev = hits[0]
    for pos in hits[1:]:
        if pos <= prev + n:
            prev = pos
        else:
            spans.append((start, prev + n))
            start = prev = pos
    spans.append((start, prev + n))

    # map word spans back to character offsets in the original generated text
    flags: list[FlaggedSection] = []
    for w_start, w_end in sorted(spans, key=lambda s: s[1] - s[0], reverse=True)[:max_flags]:
        excerpt_words = gen_words[w_start:w_end]
        excerpt = " ".join(excerpt_words)
        char_start = _char_offset(generated, excerpt_words[0], w_start)
        char_end = min(len(generated), char_start + len(excerpt) + 8)
        length = w_end - w_start
        severity = "high" if length >= 10 else "medium" if length >= 7 else "low"
        flags.append(
            FlaggedSection(
                script_excerpt=excerpt,
                source_reference="matches a passage in the source transcript",
                reason=f"{length}-word span overlaps the source; consider rephrasing",
                severity=severity,
                char_start=char_start,
                char_end=char_end,
            )
        )
    return flags


def _char_offset(text: str, first_word: str, approx_word_index: int) -> int:
    # best-effort: find the first_word occurrence near the expected position
    lowered = text.lower()
    idx = lowered.find(first_word)
    return idx if idx != -1 else 0


# --------------------------------------------------------------------------- #
# Report assembly
# --------------------------------------------------------------------------- #
def build_report(
    source: str,
    generated: str,
    source_embedding: list[float] | None = None,
    generated_embedding: list[float] | None = None,
) -> OriginalityReport:
    p = phrase_overlap(source, generated)
    d = distinctive_phrase_overlap(source, generated)
    sem = (
        cosine(source_embedding, generated_embedding)
        if source_embedding and generated_embedding
        else 0.0
    )
    struct = structural_similarity(source, generated)
    flags = find_flagged_sections(source, generated)

    # Originality score: weighted inverse of the similarity signals. Distinctive
    # phrase overlap is the strongest copy signal, so it is weighted heaviest.
    similarity = (
        0.20 * p
        + 0.40 * d
        + 0.25 * sem
        + 0.15 * struct
    )
    score = int(round((1.0 - similarity) * 100))
    score = max(0, min(100, score))

    return OriginalityReport(
        originality_score=score,
        phrase_overlap=_metric(p),
        distinctive_phrase_overlap=_metric(d),
        semantic_similarity=_metric(sem),
        structural_similarity=_metric(struct),
        flagged_sections=flags,
    )
