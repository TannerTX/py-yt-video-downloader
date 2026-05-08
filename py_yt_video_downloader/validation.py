"""Validation helpers for URLs, formats, qualities, and output directories.

The functions in this module perform quick local checks before yt-dlp starts.
They intentionally reject only obvious mistakes because yt-dlp is better suited
for handling the long tail of supported YouTube URL variants and video states.
"""

from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlparse

from .errors import ValidationError

SUPPORTED_FORMATS = ("mp4", "mp3")
SUPPORTED_QUALITIES = ("best", "1080p", "720p", "480p")
YOUTUBE_HOST_SUFFIXES = ("youtube.com", "youtu.be", "youtube-nocookie.com")


def validate_url(url: str) -> str:
    """Validate that a string looks like a usable YouTube URL.

    Args:
        url: URL supplied on the command line.

    Returns:
        The original URL when it passes basic validation.

    Raises:
        ValidationError: If the URL is empty, lacks an HTTP(S) scheme, lacks a
            hostname, or is clearly not a YouTube URL.
    """
    candidate = url.strip()
    if not candidate:
        raise ValidationError(
            "The YouTube URL is empty.",
            "Paste a full link such as https://www.youtube.com/watch?v=dQw4w9WgXcQ.",
        )

    parsed = urlparse(candidate)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValidationError(
            "The URL must be a full http:// or https:// YouTube link.",
            "Example: py-yt-video-downloader https://youtu.be/VIDEO_ID -o ./downloads",
        )

    hostname = (parsed.hostname or "").lower()
    normalized_host = hostname[4:] if hostname.startswith("www.") else hostname
    if not any(normalized_host == host or normalized_host.endswith(f".{host}") for host in YOUTUBE_HOST_SUFFIXES):
        raise ValidationError(
            "That link does not look like a YouTube URL.",
            "Use a youtube.com, music.youtube.com, youtube-nocookie.com, or youtu.be link.",
        )

    return candidate


def validate_format(format_name: str) -> str:
    """Validate the requested download format.

    Args:
        format_name: Format name supplied by argparse or another caller.

    Returns:
        The normalized lowercase format name.

    Raises:
        ValidationError: If the requested format is not supported.
    """
    normalized = format_name.lower().strip()
    if normalized not in SUPPORTED_FORMATS:
        raise ValidationError(
            f"Unsupported format '{format_name}'.",
            "Choose either 'mp4' for video or 'mp3' for audio.",
        )
    return normalized


def validate_quality(quality: str) -> str:
    """Validate the requested MP4 quality preference.

    Args:
        quality: Quality value supplied by argparse or another caller.

    Returns:
        The normalized lowercase quality value.

    Raises:
        ValidationError: If the requested quality is not supported.
    """
    normalized = quality.lower().strip()
    if normalized not in SUPPORTED_QUALITIES:
        raise ValidationError(
            f"Unsupported quality '{quality}'.",
            "Choose one of: best, 1080p, 720p, or 480p.",
        )
    return normalized


def prepare_output_directory(output: str | Path) -> Path:
    """Create and validate the output directory before downloading.

    Args:
        output: Path to the directory where downloads should be saved.

    Returns:
        Absolute, expanded ``Path`` for the validated output directory.

    Raises:
        ValidationError: If the path cannot be created, is not a directory, or
            is not writable by the current process.
    """
    output_path = Path(output).expanduser().resolve()

    try:
        output_path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ValidationError(
            f"Could not create output directory: {output_path}",
            "Check that the parent folder exists and that you have permission to write there.",
        ) from exc

    if not output_path.is_dir():
        raise ValidationError(
            f"The output path is not a directory: {output_path}",
            "Choose a folder path, not a file path.",
        )

    # os.access is a fast pre-flight check; the final write is still handled by yt-dlp.
    if not os.access(output_path, os.W_OK):
        raise ValidationError(
            f"No write permission for output directory: {output_path}",
            "Choose a writable folder or update its permissions.",
        )

    return output_path
