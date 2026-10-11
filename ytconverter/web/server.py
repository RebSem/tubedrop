"""Local web UI for tubedrop.

Spins up a minimal HTTP server on 127.0.0.1, serves a single-page UI,
and exposes JSON endpoints to inspect a YouTube / VK Video link and run a
download via yt-dlp. Progress is streamed back to the browser via
Server-Sent Events so the user sees live percentage / speed / ETA.

Deliberately uses only Python stdlib (http.server, json, threading, etc.)
to keep the dependency surface small — yt-dlp is the only runtime extra.
"""
from __future__ import annotations

import glob
import json
import os
import platform
import queue
import re
import subprocess
import sys
import threading
import time
import uuid
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import yt_dlp
from yt_dlp.postprocessor.common import PostProcessor
from yt_dlp.utils import DownloadCancelled

try:
    from yt_dlp.cookies import CookieLoadError
except ImportError:  # older yt-dlp
    class CookieLoadError(Exception):
        pass

from ytconverter import errors, formats, tools
from ytconverter.platforms import detect_platform, extract_url, platform_label
from ytconverter.web.ui import INDEX_HTML

HOST = "127.0.0.1"
DEFAULT_PORT = 8765
MAX_PORT_TRIES = 20
MAX_JOBS_KEPT = 50

# Playlists land in their own folder; single videos go straight into the
# output folder (the empty playlist component collapses to "//").
OUTTMPL = (
    "%(playlist_title,playlist_id|)s/"
    "%(playlist_index&{:03d} - |)s"
    "%(title).150B [%(id)s]"
    f"%({formats.FormatSelector.TAG_FIELD}& {{}}|)s"
    ".%(ext)s"
)

# Subtitle languages: Russian, English and the video's original language.
# Patterns like "ru.*" would also match YouTube's machine translations of
# every other track ("ru-de", "ru-ja", …) — dozens of requests and HTTP 429.
SUBTITLE_LANGS = ["ru", "en", ".*-orig"]

LIVE_STATUSES = ("is_live", "is_upcoming", "post_live")
LIVE_MESSAGE = "This is a live event — it can be downloaded after it finishes."

_jobs: dict[str, "Job"] = {}
_jobs_lock = threading.Lock()

# Set by serve() so /api/quit can shut down the running HTTPServer.
_httpd_ref: list = []
_repo_root = Path(__file__).resolve().parents[2]


def default_download_root() -> Path:
    home = Path.home()
    system = platform.system()
    if system in ("Darwin", "Windows", "Linux"):
        base = home / "Downloads"
    else:
        base = home
    return base / "tubedrop"


def folder_presets() -> list[dict]:
    """Quick-pick folders shown as chips in the UI."""
    home = Path.home()
    default_root = default_download_root()
    presets = [
        {"label": "tubedrop", "path": str(default_root)},
        {"label": "Downloads", "path": str(home / "Downloads")},
        {"label": "Desktop", "path": str(home / "Desktop")},
        {"label": "Movies", "path": str(home / "Movies")},
        {"label": "Music", "path": str(home / "Music")},
    ]
    return [p for p in presets if Path(p["path"]).exists() or p["label"] == "tubedrop"]


def pick_folder_via_dialog(initial: str | None = None) -> str | None:
    """Open a native folder picker. macOS only for now (AppleScript)."""
    if platform.system() != "Darwin":
        return None
    # Resolve the typed folder like downloads do ("~/x", "Movies/x" → home),
    # and open the dialog at its nearest existing parent. Never create
    # folders just to show a dialog.
    start = Path(os.path.expanduser((initial or "").strip())) if initial else default_download_root()
    if not start.is_absolute():
        start = Path.home() / start
    if start == default_download_root():
        try:
            start.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
    while not start.exists() and start != start.parent:
        start = start.parent
    init = str(start).replace("\\", "\\\\").replace('"', '\\"')
    script = (
        'tell application "System Events"\n'
        '  activate\n'
        '  try\n'
        '    with timeout of 3600 seconds\n'
        f'      set chosen to choose folder with prompt "Save downloads to…" '
        f'default location POSIX file "{init}"\n'
        '    end timeout\n'
        '    return POSIX path of chosen\n'
        '  on error number -128\n'
        '    return ""\n'
        '  end try\n'
        'end tell'
    )
    try:
        out = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=3700,
        )
        if out.returncode != 0:
            return None
        path = out.stdout.strip()
        return path or None
    except Exception:
        return None


def _json_response(handler: BaseHTTPRequestHandler, status: int, payload) -> None:
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(body)


def _read_json_body(handler: BaseHTTPRequestHandler):
    try:
        length = int(handler.headers.get("Content-Length") or 0)
    except ValueError:
        return None
    if length <= 0:
        return {}
    if length > 1_000_000:
        return None
    raw = handler.rfile.read(length)
    try:
        data = json.loads(raw.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _ytdlp_version() -> str:
    try:
        return yt_dlp.version.__version__
    except Exception:
        return ""


# ── cookie / browser support ─────────────────────────────────────────────
# YouTube sometimes hides HD from anonymous tools or asks "are you a bot";
# some VK videos are only visible to logged-in users. Reading the cookies of
# a browser the user is signed into fixes both.
#
# This is opt-in: the user picks a browser through the UI. We never read
# cookies until they say so. The choice is persisted in .tubedrop.config.

_CONFIG_FILE = _repo_root / ".tubedrop.config"
_APP_SUPPORT = Path.home() / "Library/Application Support"

# Browser id (as yt-dlp names it) -> (display name, candidate cookie stores).
_BROWSER_PATHS: dict[str, tuple[str, list[Path]]] = {
    "safari": ("Safari", [
        Path.home() / "Library/Containers/com.apple.Safari/Data/Library/Cookies/Cookies.binarycookies",
        Path.home() / "Library/Cookies/Cookies.binarycookies",
    ]),
    "chrome": ("Chrome", [
        _APP_SUPPORT / "Google/Chrome/Default/Cookies",
        _APP_SUPPORT / "Google/Chrome/Default/Network/Cookies",
    ]),
    "firefox": ("Firefox", [_APP_SUPPORT / "Firefox/Profiles"]),
    "brave": ("Brave", [
        _APP_SUPPORT / "BraveSoftware/Brave-Browser/Default/Cookies",
        _APP_SUPPORT / "BraveSoftware/Brave-Browser/Default/Network/Cookies",
    ]),
    "edge": ("Edge", [
        _APP_SUPPORT / "Microsoft Edge/Default/Cookies",
        _APP_SUPPORT / "Microsoft Edge/Default/Network/Cookies",
    ]),
    "opera": ("Opera", [
        _APP_SUPPORT / "com.operasoftware.Opera/Cookies",
        _APP_SUPPORT / "com.operasoftware.Opera/Default/Cookies",
    ]),
    "vivaldi": ("Vivaldi", [
        _APP_SUPPORT / "Vivaldi/Default/Cookies",
        _APP_SUPPORT / "Vivaldi/Default/Network/Cookies",
    ]),
    "chromium": ("Chromium", [
        _APP_SUPPORT / "Chromium/Default/Cookies",
        _APP_SUPPORT / "Chromium/Default/Network/Cookies",
    ]),
}


def _browser_cookie_path(browser: str) -> Path | None:
    for p in _BROWSER_PATHS[browser][1]:
        if p.exists():
            return p
    return None


_config_lock = threading.Lock()


def _load_config() -> dict:
    try:
        data = json.loads(_CONFIG_FILE.read_text())
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _save_config(cfg: dict) -> None:
    try:
        _CONFIG_FILE.write_text(json.dumps(cfg, indent=2))
    except OSError:
        pass


def _browser_list() -> list[dict]:
    """Every browser yt-dlp can read, with whether it's on this Mac."""
    mac = platform.system() == "Darwin"
    return [
        {"id": bid, "label": label, "installed": bool(mac and _browser_cookie_path(bid))}
        for bid, (label, _paths) in _BROWSER_PATHS.items()
    ]


def _detect_browsers() -> list[dict]:
    return [b for b in _browser_list() if b["installed"]]


def _connected_browser() -> str | None:
    """Currently-configured browser id, or None."""
    browser = _load_config().get("cookies_browser") or None
    return browser if browser in _BROWSER_PATHS else None


def _is_cookie_error(exc: BaseException | None) -> bool:
    seen: set[int] = set()
    stack = [exc]
    while stack:
        e = stack.pop()
        if e is None or id(e) in seen:
            continue
        seen.add(id(e))
        if isinstance(e, CookieLoadError):
            return True
        exc_info = getattr(e, "exc_info", None)
        if isinstance(exc_info, tuple) and len(exc_info) > 1:
            stack.append(exc_info[1])
        stack.append(e.__cause__)
        stack.append(e.__context__)
    return False


def _cookie_notice(exc: BaseException) -> dict:
    cause = exc
    exc_info = getattr(exc, "exc_info", None) or (None, None)
    for candidate in (exc_info[1], exc.__context__, exc.__cause__):
        if candidate is not None:
            cause = candidate
            break
    info = errors.explain(f"cookies: {cause}")
    if info["code"] not in ("cookies_permission", "cookies_failed"):
        info = errors.explain("CookieLoadError")
    browser = _connected_browser()
    label = _BROWSER_PATHS.get(browser or "", (browser or "browser", []))[0]
    info["message"] = f"{label}: {info['message']} Continued without cookies."
    return info


class _Logger:
    """Collects yt-dlp warnings/errors and mirrors them to the terminal."""

    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def debug(self, msg):
        pass

    def info(self, msg):
        pass

    def warning(self, msg):
        text = errors.clean(msg)
        if text and text not in self.warnings:
            self.warnings.append(text)
            sys.stdout.write(f"[yt-dlp] warning: {text}\n")

    def error(self, msg):
        text = errors.clean(msg)
        if text:
            self.errors.append(text)
            sys.stdout.write(f"[yt-dlp] error: {text}\n")


def _base_ydl_opts(logger: _Logger, use_cookies: bool) -> dict:
    opts: dict = {
        "logger": logger,
        "quiet": True,
        "no_warnings": False,
        "noprogress": True,
        "noplaylist": True,
        "socket_timeout": 30,
        "retries": 10,
        "fragment_retries": 10,
        "extractor_retries": 3,
        "file_access_retries": 3,
        "js_runtimes": tools.ytdlp_js_runtimes(),
    }
    location = tools.ffmpeg_location()
    if location:
        opts["ffmpeg_location"] = location
    if use_cookies:
        browser = _connected_browser()
        if browser:
            opts["cookiesfrombrowser"] = (browser,)
    return opts


def _extract(url: str, **extra) -> tuple[dict, list[dict], _Logger]:
    """extract_info(download=False) with a no-cookies retry if cookies fail."""
    notices: list[dict] = []
    attempts = [True, False] if _connected_browser() else [False]
    for with_cookies in attempts:
        logger = _Logger()
        opts = _base_ydl_opts(logger, with_cookies)
        opts.update({"skip_download": True, **extra})
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
        except Exception as e:
            if with_cookies and _is_cookie_error(e):
                notices.append(_cookie_notice(e))
                continue
            raise
        if info is None:
            raise yt_dlp.utils.DownloadError(logger.errors[-1] if logger.errors else "No video info")
        return info, notices, logger
    raise RuntimeError("unreachable")


def _pick_thumbnail(info: dict) -> str | None:
    if info.get("thumbnail"):
        return info["thumbnail"]
    thumbs = [t for t in (info.get("thumbnails") or []) if t.get("url")]
    if not thumbs:
        return None
    thumbs.sort(key=lambda t: (t.get("preference") or 0, t.get("width") or 0))
    return thumbs[-1]["url"]


def _tool_warnings(pid: str | None) -> list[dict]:
    out = []
    if not tools.ffmpeg():
        out.append({
            "code": "ffmpeg_missing",
            "message": "ffmpeg is missing or broken, so only low-quality single-file video is "
                       "available and MP3 won't work. Double-click install.command to repair it.",
        })
    if pid == "youtube" and not tools.js_runtimes():
        out.append({
            "code": "no_js_runtime",
            "message": "No JavaScript runtime (deno) found — YouTube may offer fewer qualities. "
                       "Double-click install.command to add it.",
        })
    return out


_MAX_NESTED_PLAYLISTS = 8


def _playlist_summary(info: dict) -> tuple[int, dict, list[dict], _Logger | None]:
    """Count videos and fully extract only the first one (for the ladder).

    A YouTube channel link is a playlist of tabs (/videos, /shorts, /streams)
    that are playlists themselves. Everything is listed flat, and at most one
    video is ever extracted with formats — otherwise yt-dlp would resolve
    every upload of the channel.
    """
    notices: list[dict] = []
    first_video: dict = {}
    logger: _Logger | None = None
    count = 0
    nested_budget = [_MAX_NESTED_PLAYLISTS]

    def walk(entries, depth):
        nonlocal count, first_video, logger
        for entry in entries:
            if not entry:
                continue
            url = entry.get("webpage_url") or entry.get("url")
            is_nested = entry.get("_type") == "playlist" or (
                entry.get("_type") == "url"
                and str(entry.get("ie_key") or "").endswith(("Tab", "Playlist", "UserVideos"))
            )
            if entry.get("entries") is not None:
                walk(entry["entries"], depth + 1)
                continue
            if is_nested and url and depth < 3 and nested_budget[0] > 0:
                nested_budget[0] -= 1
                try:
                    sub, more, _ = _extract(url, extract_flat="in_playlist")
                    notices.extend(more)
                    if sub.get("entries") is not None:
                        walk(sub["entries"], depth + 1)
                        continue
                except Exception:
                    continue
            count += 1
            if not first_video and url:
                try:
                    candidate, more, candidate_logger = _extract(url, extract_flat="in_playlist")
                    notices.extend(more)
                    if candidate.get("entries") is None:
                        first_video, logger = candidate, candidate_logger
                except Exception:
                    first_video = entry

    walk(info.get("entries") or [], 0)
    return count, first_video, notices, logger


def _looks_throttled(fmt_list: list, logger: _Logger) -> bool:
    """YouTube hid HD from us — as opposed to a video that is simply low-res.

    When YouTube throttles anonymous clients only the progressive 360p
    format survives; an old 240p upload still has its adaptive streams.
    """
    max_class = formats.max_quality_class(fmt_list)
    if not 0 < max_class <= 360:
        return False
    has_adaptive = any(
        formats.has_video(f) and f.get("acodec") == "none" for f in fmt_list
    )
    hints = ("missing", "po token", "sabr", "only images", "not available")
    warned = any(any(h in w.lower() for h in hints) for w in logger.warnings)
    return not has_adaptive or warned


def _fetch_info(url: str) -> dict:
    """Pull metadata + formats. Returns a UI-friendly dict."""
    pid = detect_platform(url)
    info, notices, logger = _extract(url, extract_flat="in_playlist")

    is_playlist = info.get("_type") == "playlist" or info.get("entries") is not None
    target = info
    count = 1
    if is_playlist:
        count, target, more, entry_logger = _playlist_summary(info)
        notices.extend(n for n in more if n not in notices)
        logger = entry_logger or logger
    elif info.get("live_status") in LIVE_STATUSES or info.get("is_live"):
        raise yt_dlp.utils.DownloadError(LIVE_MESSAGE)

    duration = target.get("duration")
    fmt_list = target.get("formats") or []
    can_merge = tools.ffmpeg() is not None
    video_q = formats.video_ladder(
        fmt_list, None if is_playlist else duration, can_merge, with_sizes=not is_playlist
    )
    audio_q = formats.audio_ladder(None if is_playlist else duration)

    browser = _connected_browser()
    throttled = pid == "youtube" and not browser and _looks_throttled(fmt_list, logger)

    common = {
        "platform": pid,
        "platform_label": platform_label(pid),
        "video_qualities": video_q,
        "audio_bitrates": audio_q,
        "youtube_throttled": throttled,
        "connected_browser": browser,
        "warnings": _tool_warnings(pid) + notices,
    }

    if is_playlist:
        return {
            "kind": "playlist",
            # Never fall back to the first entry's title: it reads like a single video.
            "title": info.get("title") or f"{platform_label(pid)} playlist".strip(),
            "uploader": info.get("uploader") or info.get("channel") or "",
            "count": count,
            "thumbnail": _pick_thumbnail(info) or _pick_thumbnail(target),
            "duration": None,
            "view_count": None,
            **common,
        }

    return {
        "kind": "video",
        "title": info.get("title") or "Untitled",
        "uploader": info.get("uploader") or info.get("channel") or "",
        "duration": duration,
        "thumbnail": _pick_thumbnail(info),
        "view_count": info.get("view_count"),
        "count": 1,
        **common,
    }


def _resolve_output_dir(raw: str | None) -> Path:
    if not raw or not raw.strip():
        target = default_download_root()
    else:
        target = Path(os.path.expanduser(raw.strip()))
        if not target.is_absolute():
            # "Movies/clips" means ~/Movies/clips, not a folder next to the app.
            target = Path.home() / target
    target.mkdir(parents=True, exist_ok=True)
    if not os.access(target, os.W_OK):
        raise PermissionError(f"Permission denied: {target}")
    return target


# ── download jobs ────────────────────────────────────────────────────────

_PP_STAGES = {
    "Merger": "Merging video and audio…",
    "ExtractAudio": "Converting to MP3…",
    "VideoRemuxer": "Packing into MP4…",
    "VideoConvertor": "Converting video…",
    "Metadata": "Writing title and tags…",
    "EmbedThumbnail": "Adding cover art…",
    "SubtitlesConvertor": "Converting subtitles…",
    "MoveFiles": "Finishing up…",
}


class Job:
    def __init__(self, params: dict):
        self.id = uuid.uuid4().hex
        self.params = params
        self.queue: queue.Queue = queue.Queue()
        self.cancel = threading.Event()
        self.status = "running"
        self.files: list[str] = []
        # video id -> {"temp": set of paths, "done": bool}; only items this job
        # actually downloaded, so cleanup never touches pre-existing files.
        self.items: dict[str, dict] = {}
        # Paths seen before we know which item they belong to (subtitles).
        self.loose_files: set[str] = set()
        self.live_skipped: list[str] = []
        self.cancelled = False
        self.lock = threading.Lock()
        self.created = time.time()
        self.thread: threading.Thread | None = None

    def emit(self, event: str, **data) -> None:
        self.queue.put({"event": event, **data})

    def track(self, video_id: str | None, *paths) -> None:
        with self.lock:
            if video_id:
                bucket = self.items.setdefault(video_id, {"temp": set(), "done": False})["temp"]
            else:
                bucket = self.loose_files
            for p in paths:
                if p:
                    bucket.add(str(p))

    def sidecar_paths(self, info: dict) -> list[str]:
        paths = [t.get("filepath") for t in info.get("thumbnails") or [] if isinstance(t, dict)]
        subs = info.get("requested_subtitles") or {}
        paths += [s.get("filepath") for s in subs.values() if isinstance(s, dict)]
        return [p for p in paths if p]


class _DonePP(PostProcessor):
    """Runs last for every finished item: records the final file."""

    def __init__(self, job: Job):
        super().__init__(None)
        self.job = job

    def run(self, info):
        job = self.job
        path = info.get("filepath")
        with job.lock:
            if path:
                job.files.append(os.path.normpath(str(path)))
            item = job.items.get(info.get("id"))
            if item is not None:
                item["done"] = True
            job.loose_files.clear()
        return [], info


def _item_position(info: dict) -> tuple[int | None, int | None]:
    index = info.get("playlist_index")
    count = info.get("n_entries") or info.get("playlist_count")
    if not index or not count or count <= 1:
        return None, None
    return index, count


def _make_progress_hook(job: Job, selector: formats.FormatSelector):
    last_emit = [0.0]

    def hook(d):
        status = d.get("status")
        info = d.get("info_dict") or {}
        video_id = info.get("id")
        if status == "downloading":
            # Track first: the .part file already exists when the first
            # callback fires, and a pending cancel must be able to remove it.
            job.track(video_id, d.get("tmpfilename"), d.get("filename"))
            if video_id:
                job.track(video_id, *job.sidecar_paths(info))
        if job.cancel.is_set():
            raise DownloadCancelled("Cancelled")
        if status != "downloading":
            return

        now = time.monotonic()
        if now - last_emit[0] < 0.25:
            return
        last_emit[0] = now

        downloaded = d.get("downloaded_bytes") or 0
        total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
        speed = d.get("speed")
        eta = d.get("eta")

        percent = None
        if total:
            percent = downloaded / total * 100.0
        elif d.get("fragment_count"):
            percent = (d.get("fragment_index") or 0) / d["fragment_count"] * 100.0

        # A merged download fetches video and audio one after another.
        # Report one continuous bar across both parts when sizes are known.
        choice = selector.last_choice
        reqs = choice.formats if choice else []
        ids = [f.get("format_id") for f in reqs]
        part = part_index = part_count = None
        if len(reqs) > 1 and info.get("format_id") in ids:
            part_count = len(reqs)
            part_index = ids.index(info.get("format_id"))
            current = reqs[part_index]
            part = "audio" if current.get("vcodec") == "none" else "video"
            sizes = [formats.format_size(f, info.get("duration")) for f in reqs]
            if total and all(sizes):
                before = sum(sizes[:part_index])
                grand = before + total + sum(sizes[part_index + 1:])
                downloaded = before + downloaded
                total = grand
                percent = downloaded / grand * 100.0
                if speed:
                    eta = max(0, (grand - downloaded) / speed)

        item_index, item_count = _item_position(info)
        job.emit(
            "progress",
            percent=min(percent, 100.0) if percent is not None else None,
            speed=speed,
            eta=eta,
            downloaded=downloaded,
            total=total or None,
            part=part,
            part_index=(part_index + 1) if part_index is not None else None,
            part_count=part_count,
            item_index=item_index,
            item_count=item_count,
        )

    return hook


def _make_pp_hook(job: Job):
    last = [None]

    def hook(d):
        info = d.get("info_dict") or {}
        name = d.get("postprocessor") or ""
        if name == _DonePP.pp_key():
            return  # the item is complete; let it be reported
        if d.get("status") == "started" and info.get("id") in job.items:
            # Remember what this postprocessor writes (e.g. the merged .mp4 or
            # the .mp3 ExtractAudio is about to create) *before* honouring a
            # cancel, so cleanup can remove it. Files that already exist are
            # left alone — they may be a previous finished download.
            filepath = info.get("filepath")
            outputs = []
            if filepath:
                stem = os.path.splitext(filepath)[0]
                outputs = [p for p in (stem + ".mp3", stem + ".mp4") if not os.path.exists(p)]
            job.track(info.get("id"), filepath, *outputs, *job.sidecar_paths(info))
        if job.cancel.is_set():
            raise DownloadCancelled("Cancelled")
        if d.get("status") != "started":
            return
        if name == "SubtitlesConvertor" and not info.get("requested_subtitles"):
            return
        message = _PP_STAGES.get(name)
        if not message and name.startswith("Fixup"):
            message = "Fixing up the file…"
        item_index, item_count = _item_position(info)
        key = (message, info.get("id"))
        # Some postprocessors report "started" twice; show each stage once.
        if message and key != last[0]:
            last[0] = key
            job.emit("stage", message=message, item_index=item_index, item_count=item_count)

    return hook


def _make_live_filter(job: Job):
    """Skip live streams: yt-dlp would record them forever via ffmpeg,
    without progress events and beyond the reach of the cancel button."""

    def match_filter(info, *, incomplete=False):
        if info.get("live_status") in LIVE_STATUSES or info.get("is_live"):
            title = info.get("title") or info.get("id") or "stream"
            message = f"{LIVE_MESSAGE} ({title})"
            if message not in job.live_skipped:
                job.live_skipped.append(message)
            return message
        return None

    return match_filter


def _build_download_opts(job: Job, logger: _Logger, with_cookies: bool, output_dir: Path) -> dict:
    params = job.params
    mode = params["mode"]
    can_merge = tools.ffmpeg() is not None

    selector = formats.FormatSelector(mode, params["quality"], can_merge)
    opts = _base_ydl_opts(logger, with_cookies)
    opts.update({
        "format": selector,
        "outtmpl": {"default": str(output_dir / OUTTMPL)},
        "progress_hooks": [_make_progress_hook(job, selector)],
        "postprocessor_hooks": [_make_pp_hook(job)],
        "match_filter": _make_live_filter(job),
        # Keep going past per-video problems (a failed subtitle or one broken
        # playlist entry); failures are collected by the logger instead.
        "ignoreerrors": True,
        "concurrent_fragment_downloads": 4,
    })

    postprocessors: list[dict] = []
    if mode == "mp4":
        if can_merge:
            opts["merge_output_format"] = "mp4"
            postprocessors.append({"key": "FFmpegVideoRemuxer", "preferedformat": "mp4"})
            postprocessors.append({
                "key": "FFmpegMetadata",
                "add_metadata": True,
                "add_chapters": True,
            })
    elif mode == "mp3":
        if not can_merge:
            raise yt_dlp.utils.DownloadError("ffmpeg not found: MP3 conversion needs ffmpeg")
        quality = params["quality"]
        postprocessors.extend([
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "0" if quality == "best" else quality,
            },
            {"key": "FFmpegMetadata", "add_metadata": True},
            {"key": "EmbedThumbnail", "already_have_thumbnail": False},
        ])
        opts["writethumbnail"] = True
    else:
        raise ValueError(f"Unknown mode: {mode}")

    if params.get("subtitles"):
        opts.update({
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": SUBTITLE_LANGS,
            "subtitlesformat": "srt/vtt/best",
            "extractor_args": {"youtube": {"skip": ["translated_subs"]}},
        })
        if can_merge:
            postprocessors.insert(0, {
                "key": "FFmpegSubtitlesConvertor",
                "format": "srt",
                "when": "before_dl",
            })

    opts["postprocessors"] = postprocessors
    return opts


def _cleanup_partial(job: Job) -> None:
    """Delete what unfinished items of a cancelled job left behind."""
    with job.lock:
        keep = {os.path.abspath(f) for f in job.files}
        bases = set(job.loose_files)
        for item in job.items.values():
            if not item["done"]:
                bases |= item["temp"]
    for base in bases:
        for path in glob.glob(glob.escape(base) + "*"):
            if os.path.abspath(path) in keep:
                continue
            try:
                if os.path.isfile(path):
                    os.remove(path)
            except OSError:
                pass


def _existing_files(paths: list[str]) -> list[str]:
    seen: set[str] = set()
    out = []
    for p in paths:
        key = os.path.abspath(p)
        if key in seen or not os.path.isfile(p):
            continue
        seen.add(key)
        out.append(p)
    return out


def _run_job(job: Job) -> None:
    params = job.params

    def finish(status: str, event: str, **data):
        job.status = status
        job.emit(event, **data)
        job.emit("done", ok=status == "done")

    job.emit("stage", message="Fetching video info…")
    try:
        output_dir = _resolve_output_dir(params.get("output_dir"))
    except OSError as e:
        finish("error", "error", **errors.explain(e))
        return

    logger = _Logger()
    failure: BaseException | None = None
    attempts = [True, False] if _connected_browser() else [False]
    for with_cookies in attempts:
        logger = _Logger()
        try:
            opts = _build_download_opts(job, logger, with_cookies, output_dir)
            selector = opts["format"]
            with yt_dlp.YoutubeDL(opts) as ydl:
                selector.ydl = ydl
                ydl.add_post_processor(_DonePP(job), when="after_move")
                ydl.download([params["url"]])
            failure = None
            break
        except DownloadCancelled:
            job.cancelled = True
            break
        except Exception as e:
            if with_cookies and _is_cookie_error(e) and not job.files:
                job.emit("notice", **_cookie_notice(e))
                continue
            failure = e
            break

    # A cancel that arrives after yt-dlp already finished changes nothing.
    if job.cancelled:
        _cleanup_partial(job)
        finish("cancelled", "cancelled", message="Download cancelled.")
        return

    files = _existing_files(job.files)
    if not files:
        raw = failure if failure is not None else (
            logger.errors[-1] if logger.errors
            else job.live_skipped[0] if job.live_skipped
            else "Nothing was downloaded."
        )
        if failure is not None and not isinstance(failure, yt_dlp.utils.YoutubeDLError):
            raw = f"{type(failure).__name__}: {failure}"
        finish("error", "error", **errors.explain(raw))
        return

    sizes = {}
    for f in files:
        try:
            sizes[f] = Path(f).stat().st_size
        except OSError:
            pass
    job.files = files
    failed = [errors.explain(e) for e in logger.errors + job.live_skipped]
    notices = []
    sub_failures = [w for w in logger.warnings if "unable to download video subtitles" in w.lower()]
    if params.get("subtitles") and sub_failures:
        notices.append({
            "code": "subtitles_partial",
            "message": f"{len(sub_failures)} subtitle file(s) couldn't be downloaded "
                       f"({errors.explain(sub_failures[0])['message']})",
        })
    finish(
        "done",
        "complete",
        files=files,
        sizes=sizes,
        output_dir=str(output_dir),
        failed=len(failed),
        failures=failed[:5],
        notices=notices,
    )


def _prune_jobs() -> None:
    with _jobs_lock:
        finished = sorted(
            (j for j in _jobs.values() if j.status != "running"),
            key=lambda j: j.created,
        )
        while len(_jobs) > MAX_JOBS_KEPT and finished:
            _jobs.pop(finished.pop(0).id, None)


def _defaults_payload() -> dict:
    return {
        "default_output_dir": str(default_download_root()),
        "platform": platform.system(),
        "presets": folder_presets(),
        "can_pick_folder": platform.system() == "Darwin",
        "browsers": _browser_list(),
        "connected_browser": _connected_browser(),
        "tools": tools.status(),
        "ytdlp_version": _ytdlp_version(),
        "warnings": _tool_warnings(None),
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "tubedrop/1.2"

    def log_message(self, fmt, *args):  # noqa: A003 - silence default access log
        # SSE streams and polling would flood the terminal; errors still show.
        pass

    def _safe_path(self) -> str:
        return urlparse(self.path).path

    def _request_allowed(self) -> bool:
        """Only the tubedrop page itself may call the API.

        Blocks other websites (CSRF) and DNS-rebinding tricks from driving
        downloads, reading cookies or quitting the app.
        """
        port = self.server.server_address[1]
        allowed_hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}
        host = (self.headers.get("Host") or "").lower()
        if host not in allowed_hosts:
            return False
        site = self.headers.get("Sec-Fetch-Site")
        if site and site not in ("same-origin", "none"):
            return False
        origin = self.headers.get("Origin")
        if origin and origin.lower() not in {f"http://{h}" for h in allowed_hosts}:
            return False
        return True

    def _forbidden(self):
        _json_response(self, HTTPStatus.FORBIDDEN, {"error": "Forbidden"})

    def do_GET(self):  # noqa: N802 - http.server signature
        path = self._safe_path()
        if path == "/" or path == "/index.html":
            body = INDEX_HTML.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Referrer-Policy", "no-referrer")
            # Other sites must not frame the UI and trick clicks into it.
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Content-Security-Policy", "frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(body)
            return

        if not path.startswith("/api/"):
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")
            return
        if not self._request_allowed():
            self._forbidden()
            return

        if path == "/api/defaults":
            _json_response(self, HTTPStatus.OK, _defaults_payload())
            return

        if path == "/api/pick-folder":
            self._pick_folder()
            return

        if path == "/api/browsers":
            _json_response(
                self,
                HTTPStatus.OK,
                {"browsers": _browser_list(), "connected": _connected_browser()},
            )
            return

        if path.startswith("/api/events/"):
            job_id = path.rsplit("/", 1)[-1]
            self._stream_events(job_id)
            return

        if path == "/api/reveal":
            self._reveal_path()
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def do_POST(self):  # noqa: N802
        path = self._safe_path()
        if not self._request_allowed():
            self._forbidden()
            return
        if path == "/api/inspect":
            self._inspect()
            return
        if path == "/api/download":
            self._start_download()
            return
        if path == "/api/cancel":
            self._cancel()
            return
        if path == "/api/connect-browser":
            self._connect_browser()
            return
        if path == "/api/disconnect-browser":
            self._disconnect_browser()
            return
        if path == "/api/quit":
            self._quit()
            return
        self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def _connect_browser(self):
        body = _read_json_body(self) or {}
        browser = str(body.get("browser") or "").strip().lower()
        if browser not in _BROWSER_PATHS:
            _json_response(self, HTTPStatus.BAD_REQUEST, {"error": "Unknown browser."})
            return
        if not _browser_cookie_path(browser):
            _json_response(self, HTTPStatus.BAD_REQUEST,
                           {"error": f"{_BROWSER_PATHS[browser][0]} is not installed on this Mac."})
            return
        with _config_lock:
            cfg = _load_config()
            cfg["cookies_browser"] = browser
            _save_config(cfg)
        _json_response(self, HTTPStatus.OK, {"ok": True, "connected": browser})

    def _disconnect_browser(self):
        with _config_lock:
            cfg = _load_config()
            cfg.pop("cookies_browser", None)
            _save_config(cfg)
        _json_response(self, HTTPStatus.OK, {"ok": True})

    def _quit(self):
        _json_response(self, HTTPStatus.OK, {"ok": True, "message": "Shutting down…"})

        # Shutdown in a background thread so this response can finish flushing.
        def _stop():
            time.sleep(0.2)
            with _jobs_lock:
                running = [j for j in _jobs.values() if j.status == "running"]
            for job in running:
                job.cancel.set()
            if running:
                deadline = time.monotonic() + 5
                for job in running:
                    if job.thread:
                        job.thread.join(max(0.0, deadline - time.monotonic()))
            # Clean up PID/URL files so the next launch doesn't think we're still alive.
            for name in (".tubedrop.pid", ".tubedrop.url"):
                try:
                    (_repo_root / name).unlink()
                except OSError:
                    pass
            if _httpd_ref:
                try:
                    _httpd_ref[0].shutdown()
                except Exception:
                    pass
            # Make sure the process actually exits even if there are stray threads.
            os._exit(0)

        threading.Thread(target=_stop, daemon=True).start()

    # --- handlers -------------------------------------------------------

    def _parse_url(self, body: dict) -> tuple[str, str | None]:
        url = extract_url(str(body.get("url") or ""))
        return url, detect_platform(url) if url else None

    def _inspect(self):
        body = _read_json_body(self)
        if body is None:
            _json_response(self, HTTPStatus.BAD_REQUEST, {"error": "Invalid JSON"})
            return
        url, pid = self._parse_url(body)
        if not pid:
            _json_response(
                self,
                HTTPStatus.BAD_REQUEST,
                {"error": "Paste a YouTube or VK Video link.", "code": "unsupported"},
            )
            return
        try:
            info = _fetch_info(url)
        except Exception as e:
            raw = e if isinstance(e, yt_dlp.utils.YoutubeDLError) else f"{type(e).__name__}: {e}"
            explained = errors.explain(raw)
            _json_response(
                self,
                HTTPStatus.BAD_GATEWAY,
                {
                    "error": explained["message"],
                    "code": explained["code"],
                    "detail": explained["detail"],
                    "needs_browser": explained["needs_browser"],
                    "platform": pid,
                },
            )
            return
        info["normalized_url"] = url
        _json_response(self, HTTPStatus.OK, info)

    def _start_download(self):
        body = _read_json_body(self)
        if body is None:
            _json_response(self, HTTPStatus.BAD_REQUEST, {"error": "Invalid JSON"})
            return
        url, pid = self._parse_url(body)
        if not pid:
            _json_response(self, HTTPStatus.BAD_REQUEST, {"error": "Paste a YouTube or VK Video link."})
            return
        mode = body.get("mode")
        if mode not in ("mp4", "mp3"):
            _json_response(self, HTTPStatus.BAD_REQUEST, {"error": "mode must be mp4 or mp3"})
            return
        quality = str(body.get("quality") or "best")
        if not re.fullmatch(r"best|\d{2,4}", quality):
            _json_response(self, HTTPStatus.BAD_REQUEST, {"error": "Bad quality"})
            return
        if mode == "mp3" and quality != "best" and not 32 <= int(quality) <= 320:
            quality = "best"

        job = Job({
            "url": url,
            "platform": pid,
            "mode": mode,
            "quality": quality,
            "output_dir": str(body.get("output_dir") or ""),
            "subtitles": bool(body.get("subtitles")),
        })
        _prune_jobs()
        with _jobs_lock:
            _jobs[job.id] = job
        job.thread = threading.Thread(target=_run_job, args=(job,), daemon=True)
        job.thread.start()
        _json_response(self, HTTPStatus.OK, {"job_id": job.id})

    def _cancel(self):
        body = _read_json_body(self) or {}
        with _jobs_lock:
            job = _jobs.get(str(body.get("job_id") or ""))
        if not job:
            _json_response(self, HTTPStatus.NOT_FOUND, {"error": "Unknown job"})
            return
        job.cancel.set()
        _json_response(self, HTTPStatus.OK, {"ok": True})

    def _stream_events(self, job_id: str):
        with _jobs_lock:
            job = _jobs.get(job_id)
        if not job:
            self.send_error(HTTPStatus.NOT_FOUND, "Unknown job")
            return
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "close")
        self.end_headers()

        try:
            while True:
                try:
                    msg = job.queue.get(timeout=15)
                except queue.Empty:
                    # heartbeat keeps the connection from being closed by proxies
                    self.wfile.write(b": ping\n\n")
                    self.wfile.flush()
                    continue
                data = json.dumps(msg)
                self.wfile.write(f"data: {data}\n\n".encode("utf-8"))
                self.wfile.flush()
                if msg.get("event") == "done":
                    break
        except (BrokenPipeError, ConnectionResetError):
            return

    def _pick_folder(self):
        q = parse_qs(urlparse(self.path).query)
        initial = q.get("initial", [""])[0] or None
        chosen = pick_folder_via_dialog(initial)
        if chosen is None:
            _json_response(self, HTTPStatus.OK, {"cancelled": True})
            return
        _json_response(self, HTTPStatus.OK, {"path": chosen})

    def _reveal_path(self):
        q = parse_qs(urlparse(self.path).query)
        path = q.get("path", [""])[0]
        if not path:
            _json_response(self, HTTPStatus.BAD_REQUEST, {"error": "no path"})
            return
        p = Path(path)
        if not p.exists():
            _json_response(self, HTTPStatus.NOT_FOUND, {"error": "not found"})
            return
        try:
            system = platform.system()
            if system == "Darwin":
                subprocess.Popen(["open", "-R", str(p)])
            elif system == "Windows":
                subprocess.Popen(["explorer", "/select,", str(p)])
            else:
                subprocess.Popen(["xdg-open", str(p.parent)])
        except Exception as e:
            _json_response(self, HTTPStatus.INTERNAL_SERVER_ERROR, {"error": str(e)})
            return
        _json_response(self, HTTPStatus.OK, {"ok": True})


def _find_free_port(start: int) -> int:
    import socket

    for port in range(start, start + MAX_PORT_TRIES):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Match HTTPServer.allow_reuse_address: a port left in TIME_WAIT by
            # the previous run is free, so the UI keeps its origin (and saved
            # settings) across a quick restart.
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind((HOST, port))
            except OSError:
                continue
            return port
    raise RuntimeError("No free port found")


def _print_tool_report() -> None:
    status = tools.status()
    dim, warn, reset = "\033[2m", "\033[33;1m", "\033[0m"
    print(f"{dim}  yt-dlp {_ytdlp_version()}{reset}")
    ff = status["ffmpeg"]
    if ff:
        print(f"{dim}  ffmpeg: {ff['path']}{reset}")
    else:
        print(f"{warn}  ffmpeg is missing or broken — HD video and MP3 need it. "
              f"Run install.command again.{reset}")
    js = status["js_runtime"]
    if js:
        print(f"{dim}  JS runtime: {js['name']} ({js['path']}){reset}")
    else:
        print(f"{warn}  No JavaScript runtime (deno) — YouTube may offer fewer qualities.{reset}")


def serve(open_browser: bool = True, port: int | None = None) -> None:
    tools.augment_path()

    chosen = _find_free_port(port or DEFAULT_PORT)
    httpd = ThreadingHTTPServer((HOST, chosen), Handler)
    httpd.daemon_threads = True
    _httpd_ref.append(httpd)
    url = f"http://{HOST}:{chosen}/"

    pid_file = _repo_root / ".tubedrop.pid"
    url_file = _repo_root / ".tubedrop.url"
    try:
        pid_file.write_text(str(os.getpid()))
        url_file.write_text(url)
    except OSError:
        pass

    print()
    print(f"\033[32;1m  tubedrop ready:\033[0m {url}")
    print(f"\033[2m  Default output: {default_download_root()}\033[0m")
    _print_tool_report()
    print("\033[2m  Click Quit in the browser, or close this window, to stop.\033[0m")
    print()

    if open_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\033[33;1mShutting down…\033[0m")
    finally:
        httpd.server_close()
        for f in (pid_file, url_file):
            try:
                f.unlink()
            except OSError:
                pass


if __name__ == "__main__":
    serve()
