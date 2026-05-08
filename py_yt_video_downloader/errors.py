"""Friendly exception types used by py-yt-video-downloader.

The CLI catches these exceptions and converts them into short, human-readable
messages. Keeping expected failures in one hierarchy prevents raw tracebacks for
common user-facing problems while still allowing ``--verbose`` to display full
technical details when needed.
"""

from __future__ import annotations


class DownloaderError(Exception):
    """Base class for expected py-yt-video-downloader failures.

    Args:
        message: Human-readable description of the failure.
        tip: Optional actionable advice that helps the user fix the problem.

    Attributes:
        message: Human-readable description of the failure.
        tip: Optional actionable advice that helps the user fix the problem.
    """

    def __init__(self, message: str, tip: str | None = None) -> None:
        """Initialize a downloader error with an optional troubleshooting tip.

        Args:
            message: Friendly explanation of what went wrong.
            tip: Optional next step the user can take to resolve the issue.

        Returns:
            None.
        """
        super().__init__(message)
        self.message = message
        self.tip = tip


class ValidationError(DownloaderError):
    """Raised when local command input or filesystem validation fails.

    Args:
        message: Human-readable validation failure.
        tip: Optional corrective action for the user.
    """


class DependencyError(DownloaderError):
    """Raised when a required local dependency, such as FFmpeg, is missing.

    Args:
        message: Human-readable dependency failure.
        tip: Optional installation or configuration advice.
    """


class DownloadFailedError(DownloaderError):
    """Raised when yt-dlp cannot complete the requested download.

    Args:
        message: Human-readable download failure.
        tip: Optional troubleshooting advice for network, privacy, or media
            availability issues.
    """
