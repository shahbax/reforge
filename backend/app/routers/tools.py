"""Public, no-signup utility tools — SEO lead magnets.

These endpoints require no auth and are cheap/free to run:
  * /tools/originality — source-vs-text similarity audit (our unique tool; $0, deterministic)
  * /tools/hook        — heuristic hook analysis (no LLM)
  * /tools/transcript  — pull a video's transcript (ingestion; captions-first)

A lightweight in-memory per-IP rate limit guards against abuse.
"""
from __future__ import annotations

import time
from collections import defaultdict, deque

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field

from app.schemas import OriginalityReport
from app.services.ai.provider import get_provider
from app.services.ingestion import youtube
from app.services.originality import guard

router = APIRouter(prefix="/tools", tags=["tools"])

_MAX_TEXT = 20_000

# --- simple in-memory per-IP rate limiter (public endpoints) ---
_hits: dict[str, deque] = defaultdict(deque)
_WINDOW_S = 60.0
_MAX_PER_WINDOW = 30


def _rate_limit(request: Request) -> None:
    ip = request.client.host if request.client else "unknown"
    now = time.time()
    dq = _hits[ip]
    while dq and now - dq[0] > _WINDOW_S:
        dq.popleft()
    if len(dq) >= _MAX_PER_WINDOW:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many requests — slow down a moment.")
    dq.append(now)


# --------------------------------------------------------------------------- #
# Originality / reused-content checker (our differentiator)
# --------------------------------------------------------------------------- #
class OriginalityToolRequest(BaseModel):
    source: str = Field(min_length=1, max_length=_MAX_TEXT)
    generated: str = Field(min_length=1, max_length=_MAX_TEXT)


@router.post("/originality")
def originality_tool(body: OriginalityToolRequest, request: Request) -> OriginalityReport:
    _rate_limit(request)
    emb = get_provider().embed([body.source, body.generated])
    return guard.build_report(
        source=body.source,
        generated=body.generated,
        source_embedding=emb[0],
        generated_embedding=emb[1],
    )


# --------------------------------------------------------------------------- #
# Hook analyzer (heuristic, no LLM)
# --------------------------------------------------------------------------- #
class HookToolRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


_CURIOSITY = {
    "secret", "nobody", "everyone", "never", "actually", "but", "wrong", "mistake",
    "why", "how", "truth", "hidden", "really", "surprising", "shocking", "reason",
    "myth", "stop", "avoid", "before", "until",
}
_SECOND_PERSON = {"you", "your", "you're", "yourself", "youre"}


def analyze_hook(text: str) -> dict:
    words = [w.strip(".,!?\"'").lower() for w in text.split()]
    n = len(words)
    has_q = "?" in text
    curiosity = sum(1 for w in words if w in _CURIOSITY)
    second = any(w in _SECOND_PERSON for w in words)
    has_number = any(any(c.isdigit() for c in w) for w in words)

    length_score = 30 if n <= 3 else 100 if n <= 18 else 70 if n <= 28 else 40
    strength = round(
        0.35 * length_score
        + 0.20 * (100 if has_q else 0)
        + 0.25 * min(100, curiosity * 40)
        + 0.12 * (100 if second else 0)
        + 0.08 * (100 if has_number else 0)
    )
    strength = max(0, min(100, strength))

    if has_q and curiosity:
        hook_type = "curiosity question"
    elif has_q:
        hook_type = "question"
    elif curiosity >= 2:
        hook_type = "contradiction / curiosity gap"
    elif has_number:
        hook_type = "listicle / number"
    else:
        hook_type = "statement / bold claim"

    suggestions: list[str] = []
    if not has_q and curiosity == 0:
        suggestions.append("Open with a question or a surprising claim to create a curiosity gap.")
    if not second:
        suggestions.append("Address the viewer directly with 'you' to make it personal.")
    if n > 28:
        suggestions.append("Shorten it — aim for one punchy line (under ~18 words).")
    if n <= 3:
        suggestions.append("Give a little more — too short to spark curiosity.")
    if not suggestions:
        suggestions.append("Strong hook. Test it against 2–3 alternatives to be sure.")

    return {
        "hook_type": hook_type,
        "strength": strength,
        "length_words": n,
        "has_question": has_q,
        "addresses_viewer": second,
        "curiosity_markers": curiosity,
        "suggestions": suggestions,
    }


@router.post("/hook")
def hook_tool(body: HookToolRequest, request: Request) -> dict:
    _rate_limit(request)
    return analyze_hook(body.text)


# --------------------------------------------------------------------------- #
# Transcript extractor
# --------------------------------------------------------------------------- #
class TranscriptToolRequest(BaseModel):
    url: str


@router.post("/transcript")
def transcript_tool(body: TranscriptToolRequest, request: Request) -> dict:
    _rate_limit(request)
    try:
        youtube.validate_url(body.url)
    except youtube.IngestionError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    meta, transcript = youtube.fetch(body.url)
    if transcript is None:
        from app.services.transcription.transcriber import transcribe

        transcript = transcribe(meta)
    return {
        "title": meta.title,
        "channel": meta.channel_name,
        "platform": meta.platform.value,
        "source": transcript.source,
        "word_count": len(transcript.full_text.split()),
        "transcript": transcript.full_text,
    }
