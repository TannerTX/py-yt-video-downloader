"""Module entry point for ``python -m py_yt_video_downloader``.

This file delegates to the same CLI implementation used by the installed
``py-yt-video-downloader`` console script so both execution styles behave
identically.
"""

from __future__ import annotations

from .cli import main


if __name__ == "__main__":
    raise SystemExit(main())
