"""Keep yt-dlp fresh.

YouTube and VK change their players often; a yt-dlp that is a few weeks old
is the most common reason downloads break or lose quality. Once a day, at
launch and *before* yt-dlp is imported, upgrade it inside the project venv.
"""
from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
STAMP_FILE = REPO_ROOT / ".tubedrop.ytdlp-check"
VENV_DIR = REPO_ROOT / ".venv"

CHECK_EVERY = 24 * 3600
RETRY_AFTER_FAILURE = 3600
PIP_TIMEOUT = 120


def _in_project_venv() -> bool:
    try:
        return Path(sys.prefix).resolve() == VENV_DIR.resolve()
    except OSError:
        return False


def _stamp_age() -> float:
    try:
        return time.time() - STAMP_FILE.stat().st_mtime
    except OSError:
        return float("inf")


def _touch(age_offset: float = 0.0) -> None:
    """Record a check; a positive offset makes the next check come sooner."""
    try:
        STAMP_FILE.write_text(str(int(time.time())))
        if age_offset:
            ts = time.time() - age_offset
            os.utime(STAMP_FILE, (ts, ts))
    except OSError:
        pass


def maybe_update(printer=print, force: bool = False) -> bool:
    """Upgrade yt-dlp if the last check is older than a day.

    Returns True when pip ran successfully. Never raises.
    """
    if os.environ.get("TUBEDROP_NO_UPDATE"):
        return False
    if not _in_project_venv():
        return False
    if not force and _stamp_age() < CHECK_EVERY:
        return False

    # pip exits 0 ("Requirement already satisfied") when PyPI is unreachable,
    # so check connectivity first or an offline launch would count as updated.
    try:
        socket.create_connection(("pypi.org", 443), timeout=5).close()
    except OSError:
        printer("  Couldn't reach PyPI to update yt-dlp (offline?). Will retry later.")
        _touch(age_offset=CHECK_EVERY - RETRY_AFTER_FAILURE)
        return False

    printer("  Checking for yt-dlp updates…")
    cmd = [
        sys.executable, "-m", "pip", "install",
        "--quiet", "--disable-pip-version-check",
        "--retries", "1", "--timeout", "15",
        "--upgrade", "--pre", "yt-dlp[default]",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=PIP_TIMEOUT)
    except (OSError, subprocess.SubprocessError):
        printer("  Skipped the yt-dlp update (it took too long). Will retry later.")
        _touch(age_offset=CHECK_EVERY - RETRY_AFTER_FAILURE)
        return False

    if result.returncode != 0:
        printer("  Couldn't update yt-dlp (offline?). Will retry later.")
        _touch(age_offset=CHECK_EVERY - RETRY_AFTER_FAILURE)
        return False

    _touch()
    return True
