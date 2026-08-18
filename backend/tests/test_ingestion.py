"""URL validation + SSRF allowlist."""
import pytest

from app.schemas import Platform
from app.services.ingestion import youtube


def test_youtube_watch_url():
    platform, vid = youtube.validate_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert platform == Platform.YOUTUBE
    assert vid == "dQw4w9WgXcQ"


def test_youtu_be_short_url():
    platform, vid = youtube.validate_url("https://youtu.be/dQw4w9WgXcQ")
    assert vid == "dQw4w9WgXcQ"


def test_youtube_shorts_url():
    _, vid = youtube.validate_url("https://www.youtube.com/shorts/abc123XYZ")
    assert vid == "abc123XYZ"


def test_rejects_unknown_host():
    with pytest.raises(youtube.IngestionError):
        youtube.validate_url("https://evil.example.com/watch?v=abcdef")


def test_rejects_non_http_scheme():
    with pytest.raises(youtube.IngestionError):
        youtube.validate_url("file:///etc/passwd")


def test_rejects_bad_youtube_id():
    with pytest.raises(youtube.IngestionError):
        youtube.validate_url("https://www.youtube.com/watch?v=!")
