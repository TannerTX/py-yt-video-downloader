"""Tests for local validation helpers.

Validation tests focus on obvious user-input mistakes and filesystem pre-flight
checks. yt-dlp remains responsible for deeper video availability validation.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from py_yt_video_downloader.errors import ValidationError
from py_yt_video_downloader.validation import (
    prepare_output_directory,
    validate_format,
    validate_quality,
    validate_url,
)


@pytest.mark.parametrize(
    "url",
    [
        "https://youtu.be/dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://music.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ",
    ],
)
def test_validate_url_accepts_obvious_youtube_urls(url: str) -> None:
    """Common YouTube URL forms should pass lightweight validation."""
    assert validate_url(url) == url


@pytest.mark.parametrize("url", ["", "not-a-url", "ftp://youtu.be/video", "https://example.com/video"])
def test_validate_url_rejects_obvious_invalid_urls(url: str) -> None:
    """Empty, scheme-less, unsupported-scheme, and non-YouTube URLs should fail."""
    with pytest.raises(ValidationError):
        validate_url(url)


def test_validate_format_normalizes_supported_format() -> None:
    """Supported format values should be case-insensitive and normalized."""
    assert validate_format("MP3") == "mp3"


def test_validate_quality_rejects_unknown_quality() -> None:
    """Unsupported quality values should raise a friendly validation error."""
    with pytest.raises(ValidationError):
        validate_quality("144p")


def test_prepare_output_directory_creates_missing_directory(tmp_path: Path) -> None:
    """The output directory should be created automatically when possible."""
    output_dir = tmp_path / "nested" / "downloads"

    result = prepare_output_directory(output_dir)

    assert result == output_dir.resolve()
    assert output_dir.is_dir()


def test_prepare_output_directory_rejects_file_path(tmp_path: Path) -> None:
    """A file path is invalid because downloads must target a directory."""
    file_path = tmp_path / "not-a-directory.txt"
    file_path.write_text("content", encoding="utf-8")

    with pytest.raises(ValidationError):
        prepare_output_directory(file_path)
