"""Video ingestion: URL validation, SSRF guard, metadata + captions.

Uses yt-dlp when available. In development without yt-dlp (or when a fetch
fails and mock mode is on), it degrades to a deterministic stub so the pipeline
stays runnable — production requires real ingestion.
"""
from __future__ import annotations

import ipaddress
import logging
import re
import socket
from urllib.parse import parse_qs, urlparse

from app.config import get_settings
from app.schemas import Platform, SourceVideoMeta, Transcript, TranscriptSegment

log = logging.getLogger("reforge.ingestion")

ALLOWED_HOSTS = {
    "youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be",
    "tiktok.com", "www.tiktok.com", "vm.tiktok.com",
    "instagram.com", "www.instagram.com",
}


class IngestionError(ValueError):
    pass


# --------------------------------------------------------------------------- #
# URL validation / SSRF guard
# --------------------------------------------------------------------------- #
def validate_url(url: str) -> tuple[Platform, str]:
    """Return (platform, external_id) or raise IngestionError.

    Blocks non-allowlisted hosts and hosts that resolve to private/loopback IPs
    (SSRF protection).
    """
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise IngestionError("URL must be http(s)")
    host = (parsed.hostname or "").lower()
    if host not in ALLOWED_HOSTS:
        raise IngestionError(f"Unsupported host: {host or 'unknown'}")

    _assert_public_host(host)

    if "youtube" in host or host == "youtu.be":
        return Platform.YOUTUBE, _youtube_id(parsed)
    if "tiktok" in host:
        return Platform.TIKTOK, _last_path_segment(parsed)
    if "instagram" in host:
        return Platform.INSTAGRAM, _last_path_segment(parsed)
    raise IngestionError(f"Unsupported host: {host}")


def _assert_public_host(host: str) -> None:
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        # can't resolve during offline dev; allow allowlisted hosts through
        return
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            raise IngestionError("Host resolves to a non-public address")


def _youtube_id(parsed) -> str:
    if parsed.hostname and parsed.hostname.endswith("youtu.be"):
        vid = parsed.path.lstrip("/")
    else:
        vid = (parse_qs(parsed.query).get("v", [""])[0]) or _shorts_id(parsed.path)
    if not re.fullmatch(r"[A-Za-z0-9_-]{6,20}", vid or ""):
        raise IngestionError("Could not extract a valid YouTube video id")
    return vid


def _shorts_id(path: str) -> str:
    m = re.search(r"/shorts/([A-Za-z0-9_-]+)", path)
    return m.group(1) if m else ""


def _last_path_segment(parsed) -> str:
    seg = [s for s in parsed.path.split("/") if s]
    if not seg:
        raise IngestionError("Could not extract a video id")
    return seg[-1]


# --------------------------------------------------------------------------- #
# Fetch metadata + captions
# --------------------------------------------------------------------------- #
def fetch(url: str) -> tuple[SourceVideoMeta, Transcript | None]:
    """Fetch metadata and (if available) caption-based transcript."""
    platform, external_id = validate_url(url)
    settings = get_settings()

    try:
        import yt_dlp  # type: ignore

        meta, transcript = _fetch_with_ytdlp(url, platform, external_id, yt_dlp)
        if meta.duration_seconds > settings.max_video_duration_seconds:
            raise IngestionError(
                f"Video exceeds max duration ({settings.max_video_duration_seconds}s)"
            )
        return meta, transcript
    except ImportError:
        log.warning("yt-dlp not installed; using dev stub ingestion")
    except Exception as e:  # noqa: BLE001
        log.warning("yt-dlp fetch failed (%s); using dev stub ingestion", e)

    if settings.use_mock_ai:
        return _stub(platform, external_id, url)
    raise IngestionError("Ingestion failed and mock mode is disabled")


def _fetch_with_ytdlp(url, platform, external_id, yt_dlp):  # pragma: no cover - network
    opts = {
        "quiet": True,
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtypes": "vtt",
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)

    meta = SourceVideoMeta(
        platform=platform,
        external_id=external_id,
        url=url,
        title=info.get("title", ""),
        channel_name=info.get("uploader", "") or info.get("channel", ""),
        duration_seconds=int(info.get("duration") or 0),
        published_at=info.get("upload_date"),
        view_count=info.get("view_count"),
        has_captions=bool(info.get("subtitles") or info.get("automatic_captions")),
        metadata={"description": (info.get("description") or "")[:2000]},
    )
    # Caption extraction to a full transcript is handled by the transcription
    # service (captions-first). Here we only signal availability.
    return meta, None


def _stub(platform: Platform, external_id: str, url: str) -> tuple[SourceVideoMeta, Transcript]:
    text = (
        "Here's something most people get completely wrong. You'd assume the obvious "
        "explanation is correct, but the evidence points somewhere stranger. First, "
        "consider what actually happens when you look closely. Then notice the detail "
        "everyone overlooks. That detail changes everything, and here's the surprising "
        "reason why. Once you see it, you can't unsee it. So the next time you run into "
        "this, remember what's really going on underneath."
    )
    meta = SourceVideoMeta(
        platform=platform,
        external_id=external_id,
        url=url,
        title="[dev stub] Sample source video",
        channel_name="Sample Channel",
        duration_seconds=240,
        has_captions=True,
        metadata={"note": "development stub ingestion"},
    )
    transcript = Transcript(
        language="en",
        source="mock",
        segments=[TranscriptSegment(start=0.0, end=30.0, text=text)],
        full_text=text,
        token_count=len(text.split()),
    )
    return meta, transcript
