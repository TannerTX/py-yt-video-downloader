"""Tests for local execution entry points.

These tests verify that common development invocations work without installing
console scripts, including execution by filesystem path from outside the
repository root.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_package_directory_can_run_by_filesystem_path() -> None:
    """Executing the package directory directly should show CLI help successfully."""
    package_dir = Path(__file__).resolve().parents[1] / "py_yt_video_downloader"

    result = subprocess.run(
        [sys.executable, str(package_dir), "--help"],
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode == 0
    assert "usage: py-yt-video-downloader" in result.stdout
    assert "Examples:" in result.stdout


def test_repository_directory_can_run_by_filesystem_path() -> None:
    """Executing the repository directory directly should show CLI help successfully."""
    repository_dir = Path(__file__).resolve().parents[1]

    result = subprocess.run(
        [sys.executable, str(repository_dir), "--help"],
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode == 0
    assert "usage: py-yt-video-downloader" in result.stdout
    assert "Examples:" in result.stdout
