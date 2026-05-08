"""Repository-directory entry point for py-yt-video-downloader.

This module lets users run the project directly from a checkout with commands
such as ``python /path/to/py-yt-video-downloader --help``. It delegates to the
same package CLI used by ``python -m py_yt_video_downloader`` and the installed
``py-yt-video-downloader`` console script.
"""

from __future__ import annotations

from py_yt_video_downloader.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
