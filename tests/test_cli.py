"""Tests for command-line parsing and friendly CLI error handling.

These tests avoid real network downloads. They verify argparse behavior and mock
runtime paths so the CLI can be tested quickly and deterministically.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from py_yt_video_downloader import cli
from py_yt_video_downloader.downloader import DownloadRequest
from py_yt_video_downloader.errors import DownloadFailedError


def test_parse_args_defaults_to_mp4() -> None:
    """The parser should default to MP4 and best quality when optional flags are omitted."""
    args = cli.parse_args(["https://youtu.be/dQw4w9WgXcQ", "--output", "./downloads"])

    assert args.url == "https://youtu.be/dQw4w9WgXcQ"
    assert args.output == "./downloads"
    assert args.format == "mp4"
    assert args.quality == "best"
    assert args.overwrite is False


def test_parse_args_accepts_aliases_and_flags() -> None:
    """Short aliases should parse exactly like their long-option equivalents."""
    args = cli.parse_args(
        [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "-o",
            "./downloads",
            "-f",
            "mp3",
            "--quality",
            "720p",
            "--overwrite",
            "--verbose",
        ]
    )

    assert args.format == "mp3"
    assert args.output == "./downloads"
    assert args.quality == "720p"
    assert args.overwrite is True
    assert args.verbose is True


def test_missing_output_is_malformed_command(capsys: pytest.CaptureFixture[str]) -> None:
    """A missing required output directory should exit with argparse code 2 and examples."""
    with pytest.raises(SystemExit) as exc_info:
        cli.parse_args(["https://youtu.be/dQw4w9WgXcQ"])

    assert exc_info.value.code == 2
    captured = capsys.readouterr()
    assert "Command problem" in captured.err
    assert "Examples:" in captured.err


def test_invalid_format_is_malformed_command(capsys: pytest.CaptureFixture[str]) -> None:
    """An unsupported format should be rejected before download code runs."""
    with pytest.raises(SystemExit) as exc_info:
        cli.parse_args(["https://youtu.be/dQw4w9WgXcQ", "-o", "./downloads", "--format", "wav"])

    assert exc_info.value.code == 2
    captured = capsys.readouterr()
    assert "invalid choice" in captured.err
    assert "mp3" in captured.err
    assert "mp4" in captured.err


def test_main_returns_one_for_friendly_download_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Expected downloader failures should return code 1 without a raw traceback."""

    def fake_download(_: DownloadRequest) -> None:
        """Raise a predictable download failure for CLI error handling tests."""
        raise DownloadFailedError("Network failure while contacting YouTube.", "Try again later.")

    monkeypatch.setattr(cli, "download", fake_download)

    exit_code = cli.main(["https://youtu.be/dQw4w9WgXcQ", "-o", str(tmp_path)])

    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Network failure" in captured.err
    assert "Try again later" in captured.err
    assert "Traceback" not in captured.err
