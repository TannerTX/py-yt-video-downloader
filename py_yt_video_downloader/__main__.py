"""Execution entry point for module and package-directory invocations.

This file supports two local development workflows:

* ``python -m py_yt_video_downloader --help`` when the repository root is on
  ``sys.path``.
* ``python /path/to/py_yt_video_downloader --help`` when the package directory
  itself is executed by filesystem path.

Both workflows delegate to the same CLI implementation used by the installed
``py-yt-video-downloader`` console script.
"""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    # When Python executes a package directory by path, relative imports do not
    # have package context. Add the repository root so the absolute package
    # import below works the same way it does for ``python -m`` execution.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from py_yt_video_downloader.cli import main
else:
    from .cli import main


if __name__ == "__main__":
    raise SystemExit(main())
