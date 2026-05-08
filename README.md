# py-yt-video-downloader

A simple, efficient, free Python CLI for downloading YouTube videos as **MP4** or extracting audio as **MP3**. The downloader backend is [`yt-dlp`](https://github.com/yt-dlp/yt-dlp), with a friendly command-line layer focused on clear validation, helpful errors, and safe filenames across Windows, macOS, and Linux.

> **Legal disclaimer:** Only download videos or audio that you own, that are in the public domain, or that you otherwise have permission and the legal right to download. You are responsible for following YouTube's Terms of Service and applicable law.

## Features

- Download YouTube videos as MP4.
- Extract best-available audio and convert it to MP3.
- Choose MP4 quality: `best`, `1080p`, `720p`, or `480p`.
- Automatically creates the output directory.
- Uses safe cross-platform filenames.
- Shows download progress and the final saved file path.
- Friendly error messages for malformed commands, invalid URLs, missing FFmpeg, unavailable videos, network failures, and permission problems.
- No raw stack traces unless `--verbose` is enabled.

## Requirements

- Python 3.11 or newer
- `yt-dlp` (installed automatically when installing this project)
- FFmpeg for:
  - MP3 conversion
  - reliable video/audio merging for some MP4 downloads

## Installation

### From this repository

```bash
python -m pip install .
```

For development and tests:

```bash
python -m pip install -e ".[dev]"
```

### Install dependencies manually

```bash
python -m pip install -r requirements.txt
```

Then run with Python module syntax from the repository root:

```bash
python -m py_yt_video_downloader --help
```

You can also run the checkout by filesystem path without installing it:

```bash
python /path/to/py-yt-video-downloader --help
python /path/to/py-yt-video-downloader/py_yt_video_downloader --help
```

> **Note:** Python's `-m` flag accepts an importable module name, not a filesystem path. Use `python -m py_yt_video_downloader` from the repository root, or omit `-m` when running a full path.

On Windows, the same examples work with the Python Launcher by replacing `python` with `py`, for example:

```powershell
py C:\Users\Tanner\codebase\py-yt-video-downloader --help
py C:\Users\Tanner\codebase\py-yt-video-downloader\py_yt_video_downloader --help
```

## Usage

After installation, use the console command:

```bash
py-yt-video-downloader YOUTUBE_URL --output DIRECTORY [OPTIONS]
```

### MP4 video examples

Download the best available MP4 video:

```bash
py-yt-video-downloader "https://youtu.be/VIDEO_ID" --format mp4 --output "C:\Users\Tanner\Downloads"
```

Download a video capped at 720p:

```bash
py-yt-video-downloader "https://www.youtube.com/watch?v=VIDEO_ID" -f mp4 -o ./downloads --quality 720p
```

Because MP4 is the default format, this also downloads video:

```bash
py-yt-video-downloader "https://youtu.be/VIDEO_ID" -o ./downloads
```

### MP3 audio examples

Extract the best available audio and convert it to MP3:

```bash
py-yt-video-downloader "https://youtu.be/VIDEO_ID" --format mp3 --output ./downloads
```

Using aliases:

```bash
py-yt-video-downloader "https://www.youtube.com/watch?v=VIDEO_ID" -f mp3 -o "C:\Users\Tanner\Downloads"
```

### Overwrite existing files

```bash
py-yt-video-downloader "https://youtu.be/VIDEO_ID" -o ./downloads --overwrite
```

### Verbose diagnostics

Use `--verbose` when reporting bugs or troubleshooting backend failures:

```bash
py-yt-video-downloader "https://youtu.be/VIDEO_ID" -o ./downloads --verbose
```

## CLI options

```text
positional arguments:
  YOUTUBE_URL           Required YouTube URL, such as https://youtu.be/VIDEO_ID.

options:
  -o, --output DIRECTORY
                        Required directory where the downloaded file will be saved.
  -f, --format FORMAT   Output format: mp4 or mp3. Default: mp4.
  --quality QUALITY     MP4 quality: best, 1080p, 720p, or 480p. Default: best.
  --overwrite           Overwrite existing files.
  --verbose             Show detailed diagnostic output and raw tracebacks for failures.
  --version             Show the installed version.
  -h, --help            Show help.
```

## Example terminal output

Successful MP4 download:

```text
Downloading:  42.7% at 3.10MiB/s, ETA 00:18
Download finished. Processing: /home/tanner/downloads/Example_Video_[VIDEO_ID].mp4
Saved file: /home/tanner/downloads/Example_Video_[VIDEO_ID].mp4
```

Friendly malformed command:

```text
usage: py-yt-video-downloader [-h] -o DIRECTORY [-f FORMAT] [--quality QUALITY]
                              [--overwrite] [--verbose] [--version]
                              YOUTUBE_URL

Command problem: the following arguments are required: -o/--output

How to fix it:
Examples:
  py-yt-video-downloader https://youtu.be/VIDEO_ID --format mp4 --output "C:\Users\Tanner\Downloads"
  py-yt-video-downloader https://www.youtube.com/watch?v=VIDEO_ID -f mp3 -o ./downloads
```

Missing FFmpeg for MP3:

```text
Error: FFmpeg is required to convert downloads to MP3, but it was not found.
Tip: Install FFmpeg and make sure the 'ffmpeg' command is available in your terminal.
```

## Installing FFmpeg

### Windows

Recommended options:

1. Install with Winget:

   ```powershell
   winget install Gyan.FFmpeg
   ```

2. Or install with Chocolatey:

   ```powershell
   choco install ffmpeg
   ```

After installation, open a new terminal and verify:

```powershell
ffmpeg -version
```

### macOS

Install with Homebrew:

```bash
brew install ffmpeg
ffmpeg -version
```

### Linux

Debian/Ubuntu:

```bash
sudo apt update
sudo apt install ffmpeg
ffmpeg -version
```

Fedora:

```bash
sudo dnf install ffmpeg
ffmpeg -version
```

Arch Linux:

```bash
sudo pacman -S ffmpeg
ffmpeg -version
```

## Troubleshooting

### `FFmpeg is required to convert downloads to MP3`

Install FFmpeg using the instructions above and restart your terminal. The command `ffmpeg -version` must work from the same terminal where you run `py-yt-video-downloader`.

### `The URL must be a full http:// or https:// YouTube link`

Use a complete YouTube URL, for example:

```bash
py-yt-video-downloader "https://youtu.be/VIDEO_ID" -o ./downloads
```

### `No write permission for output directory`

Choose a folder your user can write to, such as your Downloads folder, or update permissions for the target directory.

### Network, private, unavailable, or deleted videos

If yt-dlp cannot download a video, confirm that:

- Your internet connection is working.
- The video is public and still available.
- The URL opens in your browser.
- The video is not age-restricted, private, deleted, region-blocked, or members-only.

For extra details, run again with `--verbose`.

### MP4 download needs FFmpeg

Some YouTube videos provide video and audio as separate streams. yt-dlp may need FFmpeg to merge them into a final MP4 file. Install FFmpeg if a video download fails during merging.

## Development

Install in editable mode with test dependencies:

```bash
python -m pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

Run the CLI locally without installing the console script:

```bash
python -m py_yt_video_downloader "https://youtu.be/VIDEO_ID" -o ./downloads
```

Run a checkout by full filesystem path. This is useful when your terminal is not currently inside the repository:

```bash
python /path/to/py-yt-video-downloader "https://youtu.be/VIDEO_ID" -o ./downloads
python /path/to/py-yt-video-downloader/py_yt_video_downloader "https://youtu.be/VIDEO_ID" -o ./downloads
```

Do not combine `-m` with a filesystem path. For example, `python -m /path/to/py_yt_video_downloader` fails because `-m` expects a module name such as `py_yt_video_downloader`.

## Project structure

```text
__main__.py
pyproject.toml
requirements.txt
README.md
py_yt_video_downloader/
  __init__.py
  __main__.py
  cli.py
  downloader.py
  errors.py
  validation.py
tests/
  test_cli.py
  test_entrypoints.py
  test_validation.py
```
