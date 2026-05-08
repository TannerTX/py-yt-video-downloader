"""Top-level package for the py-yt-video-downloader command-line tool.

The package exposes version metadata and keeps the public import surface small.
Most users interact with the project through the ``py-yt-video-downloader``
console command, while tests and integrations can import the CLI and downloader
modules directly.

Attributes:
    __version__: Semantic version string for the installed package.
"""

from __future__ import annotations

__version__ = "0.1.0"
