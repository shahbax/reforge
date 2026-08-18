"""Transcription service — captions-first, Whisper fallback, provider-abstracted.

Order of preference (cheapest correct path first):
  1. Reuse existing captions (handled at ingestion when present).
  2. faster-whisper on extracted audio.
  3. Deepgram (or another ASR provider) — pluggable.

In development without audio/ASR available, returns a deterministic stub so the
pipeline stays runnable. Production configures a real ASR path.
"""
from __future__ import annotations

import logging

from app.config import get_settings
from app.schemas import SourceVideoMeta, Transcript, TranscriptSegment

log = logging.getLogger("reforge.transcription")


def transcribe(meta: SourceVideoMeta) -> Transcript:
    settings = get_settings()

    # Real ASR would run here (faster-whisper on the extracted audio file).
    # Kept behind availability checks so the app runs without heavy deps in dev.
    try:
        return _whisper_transcribe(meta)
    except Exception as e:  # noqa: BLE001
        log.warning("Whisper unavailable (%s)", e)

    if settings.use_mock_ai:
        return _stub(meta)
    raise RuntimeError("No transcript available and ASR is not configured")


def _whisper_transcribe(meta: SourceVideoMeta) -> Transcript:  # pragma: no cover - heavy dep
    from faster_whisper import WhisperModel  # type: ignore

    # Audio path would be produced by the ingestion step (ffmpeg extraction).
    audio_path = meta.metadata.get("audio_path")
    if not audio_path:
        raise RuntimeError("no audio path for whisper")
    model = WhisperModel("base", compute_type="int8")
    segments, info = model.transcribe(audio_path)
    segs, texts = [], []
    for s in segments:
        segs.append(TranscriptSegment(start=s.start, end=s.end, text=s.text.strip()))
        texts.append(s.text.strip())
    full = " ".join(texts)
    return Transcript(
        language=info.language or "en",
        source="whisper",
        segments=segs,
        full_text=full,
        token_count=len(full.split()),
    )


def _stub(meta: SourceVideoMeta) -> Transcript:
    text = (
        "In this video the creator opens with a bold claim, then walks through the "
        "reasoning step by step, building tension before delivering a satisfying payoff."
    )
    return Transcript(
        language="en",
        source="mock",
        segments=[TranscriptSegment(start=0.0, end=20.0, text=text)],
        full_text=text,
        token_count=len(text.split()),
    )
