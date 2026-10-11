"""Find the external helpers yt-dlp relies on and make sure they really run.

A binary that merely exists is not enough: a Homebrew upgrade can leave
ffmpeg linked against a library that is gone, and then yt-dlp silently
falls back to low-quality single-file formats. So every candidate is
executed once (``-version``) before we trust it.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import threading
import time
from dataclasses import asdict, dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BIN_DIR = REPO_ROOT / ".bin"

_SYSTEM_DIRS = (Path("/opt/homebrew/bin"), Path("/usr/local/bin"))

# yt-dlp's minimum supported versions for its YouTube JS challenge solver.
_JS_MIN_VERSIONS = {
    "deno": (2, 3, 0),
    "node": (22, 0, 0),
    "bun": (1, 2, 11),
}

# Re-check missing tools at most this often, so running install.command
# while tubedrop is open gets picked up without a restart.
_NEGATIVE_TTL = 30.0


@dataclass(frozen=True)
class Tool:
    name: str
    path: str
    version: str

    def as_dict(self) -> dict:
        return asdict(self)


def _run_version(path: Path, arg: str) -> str | None:
    try:
        out = subprocess.run(
            [str(path), arg],
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    text = (out.stdout or out.stderr or "").strip()
    return text.splitlines()[0] if text else ""


def _unique_existing(paths) -> list[Path]:
    seen: set[str] = set()
    result = []
    for p in paths:
        if not p:
            continue
        p = Path(p).expanduser()
        key = str(p)
        if key in seen:
            continue
        seen.add(key)
        # exists() follows symlinks, so broken links are skipped here.
        if p.exists() and not p.is_dir():
            result.append(p)
    return result


def _parse_version(text: str) -> tuple[int, ...]:
    m = re.search(r"(\d+)\.(\d+)(?:\.(\d+))?", text or "")
    if not m:
        return ()
    return tuple(int(x) for x in m.groups(default="0"))


class _Cache:
    def __init__(self):
        self._lock = threading.Lock()
        self._values: dict[str, tuple[float, object]] = {}

    def get(self, key, compute):
        with self._lock:
            hit = self._values.get(key)
            if hit is not None:
                stamp, value = hit
                found = value.get("ffmpeg") if isinstance(value, dict) else value
                if found or time.monotonic() - stamp < _NEGATIVE_TTL:
                    return value
        value = compute()
        with self._lock:
            self._values[key] = (time.monotonic(), value)
        return value

    def clear(self):
        with self._lock:
            self._values.clear()


_cache = _Cache()


def _ffmpeg_dirs() -> list[Path]:
    dirs = [BIN_DIR]
    which = shutil.which("ffmpeg")
    if which:
        dirs.append(Path(which).parent)
    dirs.extend(_SYSTEM_DIRS)
    out, seen = [], set()
    for d in dirs:
        if str(d) not in seen:
            seen.add(str(d))
            out.append(d)
    return out


def _find_ffmpeg_pair() -> dict:
    """Pick one directory for yt-dlp's ``ffmpeg_location``.

    yt-dlp looks for ffprobe next to ffmpeg, so a directory where both run
    wins over one that only has a working ffmpeg.
    """
    first_ffmpeg = None
    for d in _ffmpeg_dirs():
        ffmpeg = d / "ffmpeg"
        if not (ffmpeg.exists() and not ffmpeg.is_dir()):
            continue
        version = _run_version(ffmpeg, "-version")
        if version is None:
            continue
        found = Tool("ffmpeg", str(ffmpeg), version)
        ffprobe = d / "ffprobe"
        probe_version = _run_version(ffprobe, "-version") if ffprobe.exists() else None
        if probe_version is not None:
            return {"ffmpeg": found, "ffprobe": Tool("ffprobe", str(ffprobe), probe_version)}
        if first_ffmpeg is None:
            first_ffmpeg = found
    return {"ffmpeg": first_ffmpeg, "ffprobe": None}


def ffmpeg() -> Tool | None:
    return _cache.get("ffmpeg", _find_ffmpeg_pair)["ffmpeg"]


def ffprobe() -> Tool | None:
    return _cache.get("ffmpeg", _find_ffmpeg_pair)["ffprobe"]


def _js_candidates(name: str) -> list[Path]:
    home = Path.home()
    paths: list = [BIN_DIR / name, shutil.which(name)]
    paths.extend(d / name for d in _SYSTEM_DIRS)
    if name == "deno":
        paths.append(home / ".deno/bin/deno")
    elif name == "bun":
        paths.append(home / ".bun/bin/bun")
    elif name == "node":
        paths.append(home / ".volta/bin/node")
        nvm = home / ".nvm/versions/node"
        if nvm.is_dir():
            installs = sorted(
                nvm.iterdir(),
                key=lambda p: _parse_version(p.name),
                reverse=True,
            )
            paths.extend(p / "bin/node" for p in installs)
    return _unique_existing(paths)


def _find_js_runtimes() -> list[Tool]:
    found = []
    for name, minimum in _JS_MIN_VERSIONS.items():
        for path in _js_candidates(name):
            out = _run_version(path, "--version")
            if out is None:
                continue
            if _parse_version(out) >= minimum:
                found.append(Tool(name, str(path), out))
                break
    return found


def js_runtimes() -> list[Tool]:
    """Working JavaScript runtimes, best first (deno is yt-dlp's default)."""
    return _cache.get("js", _find_js_runtimes)


def ytdlp_js_runtimes() -> dict:
    """Value for yt-dlp's ``js_runtimes`` option."""
    runtimes = js_runtimes()
    if not runtimes:
        return {"deno": {}}
    return {t.name: {"path": t.path} for t in runtimes}


def ffmpeg_location() -> str | None:
    tool = ffmpeg()
    if not tool:
        return None
    return str(Path(tool.path).parent)


def status() -> dict:
    ff = ffmpeg()
    fp = ffprobe()
    js = js_runtimes()
    return {
        "ffmpeg": ff.as_dict() if ff else None,
        "ffprobe": fp.as_dict() if fp else None,
        "js_runtime": js[0].as_dict() if js else None,
    }


def refresh() -> None:
    _cache.clear()


def augment_path() -> None:
    """Make sure subprocesses spawned by yt-dlp see our bundled binaries."""
    parts = [p for p in os.environ.get("PATH", "").split(os.pathsep) if p]
    if str(BIN_DIR) not in parts:
        parts.insert(0, str(BIN_DIR))
    for d in map(str, _SYSTEM_DIRS):
        if d not in parts:
            parts.append(d)
    os.environ["PATH"] = os.pathsep.join(parts)
