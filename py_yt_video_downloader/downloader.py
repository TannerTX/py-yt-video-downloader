"""yt-dlp integration for downloading YouTube media as MP4 or MP3.

This module builds yt-dlp option dictionaries, translates progress hooks into
friendly terminal output, and converts backend exceptions into project-specific
errors that the CLI can present without raw stack traces.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import DependencyError, DownloadFailedError
from .validation import prepare_output_directory, validate_format, validate_quality, validate_url


@dataclass(frozen=True)
class DownloadRequest:
    """Validated download request passed from the CLI to the downloader.

    Args:
        url: Full YouTube URL to download.
        output_dir: Directory where the completed media file should be saved.
        format_name: Either ``mp4`` for video or ``mp3`` for extracted audio.
        quality: MP4 quality preference. Ignored for MP3 downloads.
        overwrite: Whether existing files may be overwritten by yt-dlp.
        verbose: Whether detailed backend output should be shown.

    Attributes:
        url: Full YouTube URL to download.
        output_dir: Directory where the completed media file should be saved.
        format_name: Either ``mp4`` for video or ``mp3`` for extracted audio.
        quality: MP4 quality preference. Ignored for MP3 downloads.
        overwrite: Whether existing files may be overwritten by yt-dlp.
        verbose: Whether detailed backend output should be shown.
    """

    url: str
    output_dir: Path
    format_name: str = "mp4"
    quality: str = "best"
    overwrite: bool = False
    verbose: bool = False


def build_request(
    url: str,
    output: str | Path,
    format_name: str = "mp4",
    quality: str = "best",
    overwrite: bool = False,
    verbose: bool = False,
) -> DownloadRequest:
    """Validate raw CLI values and create a ``DownloadRequest``.

    Args:
        url: Raw URL value supplied by the user.
        output: Raw output directory value supplied by the user.
        format_name: Requested media format.
        quality: Requested MP4 quality preference.
        overwrite: Whether existing output files may be overwritten.
        verbose: Whether verbose diagnostics should be enabled.

    Returns:
        A fully validated ``DownloadRequest`` instance.

    Raises:
        ValidationError: If URL, output directory, format, or quality validation
            fails.
    """
    return DownloadRequest(
        url=validate_url(url),
        output_dir=prepare_output_directory(output),
        format_name=validate_format(format_name),
        quality=validate_quality(quality),
        overwrite=overwrite,
        verbose=verbose,
    )


def ensure_ffmpeg_available() -> None:
    """Verify that FFmpeg is available for MP3 conversion.

    Args:
        None.

    Returns:
        None.

    Raises:
        DependencyError: If the ``ffmpeg`` executable cannot be found on PATH.
    """
    if shutil.which("ffmpeg") is None:
        raise DependencyError(
            "FFmpeg is required to convert downloads to MP3, but it was not found.",
            "Install FFmpeg and make sure the 'ffmpeg' command is available in your terminal.",
        )


def progress_hook(status: dict[str, Any]) -> None:
    """Print concise progress updates from yt-dlp hook payloads.

    Args:
        status: Progress dictionary supplied by yt-dlp. Common keys include
            ``status``, ``_percent_str``, ``_speed_str``, ``_eta_str``, and
            ``filename``.

    Returns:
        None.
    """
    state = status.get("status")
    if state == "downloading":
        percent = str(status.get("_percent_str", "0.0%")).strip()
        speed = str(status.get("_speed_str", "unknown speed")).strip()
        eta = str(status.get("_eta_str", "unknown ETA")).strip()
        print(f"Downloading: {percent} at {speed}, ETA {eta}", end="\r", flush=True)
    elif state == "finished":
        filename = status.get("filename") or "downloaded file"
        # Print a newline because downloading updates are written with carriage returns.
        print(f"\nDownload finished. Processing: {filename}")


def build_ydl_options(request: DownloadRequest) -> dict[str, Any]:
    """Build a yt-dlp options dictionary for a validated request.

    Args:
        request: Validated download request.

    Returns:
        Dictionary of options accepted by ``yt_dlp.YoutubeDL``.
    """
    output_template = str(request.output_dir / "%(title).200B [%(id)s].%(ext)s")
    base_options: dict[str, Any] = {
        "outtmpl": output_template,
        "restrictfilenames": True,
        "windowsfilenames": True,
        "noprogress": True,
        "progress_hooks": [progress_hook],
        "overwrites": request.overwrite,
        "continuedl": not request.overwrite,
        "quiet": not request.verbose,
        "no_warnings": not request.verbose,
    }

    if request.format_name == "mp3":
        base_options.update(
            {
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "0",
                    }
                ],
            }
        )
        return base_options

    quality_format = _mp4_format_selector(request.quality)
    base_options.update(
        {
            "format": quality_format,
            "merge_output_format": "mp4",
            "postprocessors": [
                {
                    "key": "FFmpegVideoConvertor",
                    "preferedformat": "mp4",
                }
            ],
        }
    )
    return base_options


def download(request: DownloadRequest) -> Path | None:
    """Download a YouTube video or audio track using yt-dlp.

    Args:
        request: Validated download request containing URL, output path, format,
            quality, overwrite behavior, and verbosity preference.

    Returns:
        Path to the final file when yt-dlp reports one, otherwise ``None``.

    Raises:
        DependencyError: If MP3 output is requested without FFmpeg installed.
        DownloadFailedError: If yt-dlp is unavailable or fails to download the
            requested media.
    """
    if request.format_name == "mp3":
        ensure_ffmpeg_available()

    try:
        # Import lazily so argument-parsing tests and help output do not require yt-dlp at import time.
        from yt_dlp import DownloadError, YoutubeDL
    except ImportError as exc:
        raise DependencyError(
            "yt-dlp is not installed.",
            "Install the project with 'python -m pip install .' or run 'python -m pip install yt-dlp'.",
        ) from exc

    options = build_ydl_options(request)
    try:
        with YoutubeDL(options) as ydl:
            info = ydl.extract_info(request.url, download=True)
            final_path = _extract_final_path(info)
    except DownloadError as exc:
        raise DownloadFailedError(
            "yt-dlp could not download this video.",
            "Check your network connection and confirm the video is public, available, and not deleted.",
        ) from exc
    except OSError as exc:
        raise DownloadFailedError(
            "The download failed while writing or processing the file.",
            "Check disk space, output-folder permissions, and whether FFmpeg is installed for media merging.",
        ) from exc

    if final_path is not None:
        print(f"Saved file: {final_path}")
    else:
        print(f"Download completed. Check your output directory: {request.output_dir}")
    return final_path


def _mp4_format_selector(quality: str) -> str:
    """Return a yt-dlp format selector for an MP4 quality preference.

    Args:
        quality: Validated quality value: ``best``, ``1080p``, ``720p``, or
            ``480p``.

    Returns:
        A yt-dlp format selector string that prefers MP4-compatible video and
        audio while allowing fallback formats that can be merged into MP4.
    """
    if quality == "best":
        return "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best[ext=mp4]/best"

    # Numeric quality flags are treated as maximum heights, not exact-only heights.
    max_height = quality.removesuffix("p")
    return (
        f"bestvideo[height<={max_height}][ext=mp4]+bestaudio[ext=m4a]/"
        f"bestvideo[height<={max_height}]+bestaudio/"
        f"best[height<={max_height}][ext=mp4]/best[height<={max_height}]"
    )


def _extract_final_path(info: dict[str, Any] | None) -> Path | None:
    """Extract the most likely final media path from yt-dlp info data.

    Args:
        info: Information dictionary returned by ``YoutubeDL.extract_info``.

    Returns:
        A ``Path`` for the final media file if yt-dlp exposes one, otherwise
        ``None``.
    """
    if not info:
        return None

    requested_downloads = info.get("requested_downloads") or []
    if requested_downloads:
        filepath = requested_downloads[0].get("filepath")
        if filepath:
            return Path(filepath)

    filepath = info.get("filepath") or info.get("_filename")
    return Path(filepath) if filepath else None
