"""Originality Guard is a deterministic, offline-testable algorithm."""
from app.services.originality import guard


def test_identical_text_scores_low_originality():
    text = (
        "the quick brown fox jumps over the lazy dog and then keeps on running "
        "down the hill past the old barn and into the wide open field"
    )
    report = guard.build_report(text, text, [1.0, 0.0], [1.0, 0.0])
    assert report.originality_score < 40
    assert report.flagged_sections  # verbatim overlap is located
    assert report.phrase_overlap.band == "HIGH"


def test_disjoint_text_scores_high_originality():
    a = "alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu"
    b = "one two three four five six seven eight nine ten eleven twelve thirteen"
    report = guard.build_report(a, b, [1.0, 0.0], [0.0, 1.0])
    assert report.originality_score > 70
    assert not report.flagged_sections


def test_metric_bands_are_bounded():
    report = guard.build_report("a b c d e f", "a b c x y z", [1.0], [1.0])
    for metric in (
        report.phrase_overlap,
        report.distinctive_phrase_overlap,
        report.semantic_similarity,
        report.structural_similarity,
    ):
        assert 0.0 <= metric.value <= 1.0
        assert metric.band in {"LOW", "MODERATE", "HIGH"}
