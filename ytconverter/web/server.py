"""Local web UI for ytconverter.

Spins up a minimal HTTP server on 127.0.0.1, serves a single-page UI,
and exposes JSON endpoints to inspect a YouTube URL and run a download
via yt-dlp. Progress is streamed back to the browser via Server-Sent
Events so the user sees live percentage / speed / ETA in the page.

Deliberately uses only Python stdlib (http.server, json, threading, etc.)
to keep the dependency surface small — yt-dlp is the only runtime extra.
"""
from __future__ import annotations

import json
import os
import platform
import queue
import re
import shutil
import subprocess
import sys
import threading
import time
import uuid
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

import yt_dlp

from ytconverter.constants import URL_RE
from ytconverter.utils import sanitize
from ytconverter.web.ui import INDEX_HTML

HOST = "127.0.0.1"
DEFAULT_PORT = 8765
MAX_PORT_TRIES = 20

# job_id -> {"queue": Queue, "thread": Thread, "status": str, "file": str|None}
_jobs: dict[str, dict] = {}
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
    return [p for p in presets if Path(p["path"]).parent.exists() or p["label"] == "tubedrop"]


def pick_folder_via_dialog(initial: str | None = None) -> str | None:
    """Open a native folder picker. macOS only for now (AppleScript)."""
    if platform.system() != "Darwin":
        return None
    init = initial or str(default_download_root())
    # Make sure the initial dir exists or AppleScript errors out.
    try:
        Path(init).mkdir(parents=True, exist_ok=True)
    except Exception:
        init = str(Path.home())
    script = (
        'tell application "System Events"\n'
        '  activate\n'
        '  try\n'
        f'    set chosen to choose folder with prompt "Save downloads to…" '
        f'default location POSIX file "{init}"\n'
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
            timeout=120,
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
    length = int(handler.headers.get("Content-Length") or 0)
    if length <= 0:
        return {}
    raw = handler.rfile.read(length)
    try:
        return json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError:
        return None


def _normalize_url(url: str) -> str:
    url = url.strip()
    if not url:
        return ""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


# ── cookie / HD-unlock support ──────────────────────────────────────────
# YouTube SABR-blocks anonymous yt-dlp requests on many videos — only the
# legacy 360p format comes back. Passing logged-in cookies (and letting
# yt-dlp fall back to the HLS manifest) unlocks the full quality ladder.
#
# This is opt-in: the user picks a browser through the UI. We never read
# cookies until they say so. The choice is persisted in .tubedrop.config.

_CONFIG_FILE = _repo_root / ".tubedrop.config"

# Browser id -> (display name, list of candidate cookie-store paths on macOS).
# Safari moved into Containers/ in macOS 14, but older systems still use the
# pre-sandbox location.
_BROWSER_PATHS: dict[str, tuple[str, list[Path]]] = {
    "safari":  ("Safari",  [
        Path.home() / "Library/Containers/com.apple.Safari/Data/Library/Cookies/Cookies.binarycookies",
        Path.home() / "Library/Cookies/Cookies.binarycookies",
    ]),
    "chrome":  ("Chrome",  [Path.home() / "Library/Application Support/Google/Chrome/Default/Cookies"]),
    "brave":   ("Brave",   [Path.home() / "Library/Application Support/BraveSoftware/Brave-Browser/Default/Cookies"]),
    "edge":    ("Edge",    [Path.home() / "Library/Application Support/Microsoft Edge/Default/Cookies"]),
    "firefox": ("Firefox", [Path.home() / "Library/Application Support/Firefox/Profiles"]),
}


def _browser_cookie_path(browser: str) -> Path | None:
    for p in _BROWSER_PATHS[browser][1]:
        if p.exists():
            return p
    return None


def _load_config() -> dict:
    try:
        return json.loads(_CONFIG_FILE.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_config(cfg: dict) -> None:
    try:
        _CONFIG_FILE.write_text(json.dumps(cfg, indent=2))
    except Exception:
        pass


def _detect_browsers() -> list[dict]:
    """List browsers whose cookie store exists on this machine."""
    if platform.system() != "Darwin":
        return []
    out = []
    for bid, (label, _paths) in _BROWSER_PATHS.items():
        if _browser_cookie_path(bid):
            out.append({"id": bid, "label": label})
    return out


def _connected_browser() -> str | None:
    """Currently-configured browser id, or None."""
    return _load_config().get("cookies_browser") or None


def _base_ydl_opts(use_cookies: bool = True) -> dict:
    """Common yt-dlp options. If a browser is connected, read its cookies
    (this is what unlocks HD)."""
    opts: dict = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": False,
    }
    if use_cookies:
        browser = _connected_browser()
        if browser:
            opts["cookiesfrombrowser"] = (browser,)
    return opts


def _fetch_info(url: str) -> dict:
    """Pull metadata + formats. Returns a UI-friendly dict."""
    opts = _base_ydl_opts()
    opts["skip_download"] = True
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)

    is_playlist = info.get("_type") == "playlist" or "entries" in info
    target = info
    if is_playlist:
        entries = [e for e in (info.get("entries") or []) if e]
        target = entries[0] if entries else {}

    vq = _collect_video_qualities(target)
    aq = _collect_audio_bitrates(target)

    # SABR-throttled videos return only the legacy mp4 format 18 (360p).
    # If the max real height we see is ≤ 360, surface a flag so the UI can
    # offer to connect a browser. We don't auto-do anything.
    real_heights = [int(q["value"]) for q in vq if q["value"].isdigit()]
    max_h = max(real_heights) if real_heights else 0
    throttled = (max_h <= 360) and (_connected_browser() is None)

    if is_playlist:
        return {
            "kind": "playlist",
            "title": info.get("title") or target.get("title") or "Playlist",
            "uploader": info.get("uploader") or "",
            "count": len([e for e in (info.get("entries") or []) if e]),
            "thumbnail": target.get("thumbnail"),
            "duration": None,
            "view_count": None,
            "video_qualities": vq,
            "audio_bitrates": aq,
            "youtube_throttled": throttled,
            "connected_browser": _connected_browser(),
        }

    return {
        "kind": "video",
        "title": info.get("title") or "Untitled",
        "uploader": info.get("uploader") or info.get("channel") or "",
        "duration": info.get("duration"),
        "thumbnail": info.get("thumbnail"),
        "view_count": info.get("view_count"),
        "count": 1,
        "video_qualities": vq,
        "audio_bitrates": aq,
        "youtube_throttled": throttled,
        "connected_browser": _connected_browser(),
    }


def _best_audio_filesize(info: dict) -> int | None:
    """Pick the largest audio-only stream's filesize to add to video estimates."""
    best = 0
    for f in info.get("formats", []):
        if (
            f.get("acodec") and f.get("acodec") != "none"
            and f.get("vcodec") == "none"
        ):
            sz = f.get("filesize") or f.get("filesize_approx") or 0
            if sz and sz > best:
                best = sz
    return best or None


def _collect_video_qualities(info: dict) -> list[dict]:
    """Group video formats by height.

    Two kinds of formats reach us:
      * Adaptive video-only streams (need separate audio merged in).
      * Muxed/HLS streams that already include audio.

    We pick the largest file per height across both, then add audio size
    on top only when the stream is video-only.
    """
    audio_size = _best_audio_filesize(info) or 0
    by_height: dict[int, int] = {}  # height -> best estimated total size

    for f in info.get("formats", []):
        vcodec = f.get("vcodec")
        h = f.get("height")
        if not h or not vcodec or vcodec == "none":
            continue
        sz = f.get("filesize") or f.get("filesize_approx") or 0
        if sz:
            has_audio = f.get("acodec") and f.get("acodec") != "none"
            total = sz if has_audio else sz + audio_size
            by_height[h] = max(by_height.get(h, 0), total)
        elif h not in by_height:
            by_height[h] = 0

    out = [{"value": "best", "label": "best", "size_estimate": None}]
    for h in sorted(by_height.keys()):
        sz = by_height[h]
        label = "4K" if h >= 2160 else f"{h}p"
        out.append({
            "value": str(h),
            "label": label,
            "size_estimate": sz or None,
        })
    return out


def _collect_audio_bitrates(info: dict) -> list[dict]:
    rows: list[tuple[int, int]] = []  # (abr, filesize)
    for f in info.get("formats", []):
        if (
            f.get("acodec") and f.get("acodec") != "none"
            and f.get("vcodec") == "none"
            and f.get("abr")
        ):
            sz = f.get("filesize") or f.get("filesize_approx") or 0
            rows.append((int(f["abr"]), sz))
    # de-dup by abr, keep largest filesize
    best: dict[int, int] = {}
    for abr, sz in rows:
        if abr not in best or sz > best[abr]:
            best[abr] = sz
    out = [{"value": "best", "label": "best", "size_estimate": None}]
    for abr in sorted(best.keys()):
        out.append({
            "value": str(abr),
            "label": f"{abr}",
            "size_estimate": best[abr] or None,
        })
    return out


def _resolve_output_dir(raw: str | None) -> Path:
    if not raw or not raw.strip():
        target = default_download_root()
    else:
        target = Path(os.path.expanduser(raw.strip()))
    target.mkdir(parents=True, exist_ok=True)
    return target


def _build_ydl_opts(mode: str, quality: str, output_dir: Path, with_subs: bool, progress_hook) -> dict:
    outtmpl = str(output_dir / "%(title).80B [%(id)s].%(ext)s")
    opts = _base_ydl_opts()
    opts.update({
        "outtmpl": outtmpl,
        "restrictfilenames": False,
        "noprogress": True,
        "progress_hooks": [progress_hook],
        "ignoreerrors": "only_download",
        "concurrent_fragment_downloads": 4,
        "retries": 5,
    })

    if mode == "mp4":
        if quality == "best":
            fmt = "bestvideo*+bestaudio/best"
        else:
            fmt = (
                f"bestvideo[height<={quality}]+bestaudio/"
                f"best[height<={quality}]/best"
            )
        opts["format"] = fmt
        opts["merge_output_format"] = "mp4"
        opts["postprocessors"] = [
            {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"},
        ]
    elif mode == "mp3":
        opts["format"] = "bestaudio/best"
        pp = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "0" if quality == "best" else str(quality),
            }
        ]
        opts["postprocessors"] = pp
    else:
        raise ValueError(f"Unknown mode: {mode}")

    if with_subs:
        opts.update(
            {
                "writesubtitles": True,
                "writeautomaticsub": True,
                "subtitleslangs": ["all"],
                "subtitlesformat": "srt/best",
            }
        )

    return opts


def _run_job(job_id: str, params: dict) -> None:
    q: queue.Queue = _jobs[job_id]["queue"]

    def emit(event: str, **data):
        q.put({"event": event, **data})

    url = params["url"]
    mode = params["mode"]
    quality = params["quality"]
    output_dir = _resolve_output_dir(params.get("output_dir"))
    with_subs = bool(params.get("subtitles"))

    finished_files: list[str] = []
    last_emit = [0.0]

    def progress_hook(d):
        status = d.get("status")
        if status == "downloading":
            # throttle to ~5/s so the SSE stream stays light
            now = time.time()
            if now - last_emit[0] < 0.2:
                return
            last_emit[0] = now
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes") or 0
            percent = (downloaded / total * 100.0) if total else None
            emit(
                "progress",
                percent=percent,
                speed=d.get("speed"),
                eta=d.get("eta"),
                downloaded=downloaded,
                total=total or None,
                filename=d.get("filename"),
            )
        elif status == "finished":
            emit("stage", message="Post-processing (merge / convert)…")
            fn = d.get("filename")
            if fn:
                finished_files.append(fn)

    emit("stage", message="Fetching metadata…")

    try:
        opts = _build_ydl_opts(mode, quality, output_dir, with_subs, progress_hook)
        emit("stage", message="Starting download…")
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
    except yt_dlp.utils.DownloadError as e:
        with _jobs_lock:
            _jobs[job_id]["status"] = "error"
        emit("error", message=str(e))
        emit("done", ok=False)
        return
    except Exception as e:
        with _jobs_lock:
            _jobs[job_id]["status"] = "error"
        emit("error", message=f"{type(e).__name__}: {e}")
        emit("done", ok=False)
        return

    # Resolve the final on-disk file (yt-dlp post-processing changes the extension).
    final_files = _resolve_final_files(finished_files, output_dir, mode)
    sizes = {}
    for f in final_files:
        try:
            sizes[f] = Path(f).stat().st_size
        except Exception:
            pass

    with _jobs_lock:
        _jobs[job_id]["status"] = "done"
        _jobs[job_id]["files"] = final_files

    emit(
        "complete",
        files=final_files,
        sizes=sizes,
        output_dir=str(output_dir),
    )
    emit("done", ok=True)


def _resolve_final_files(intermediate: list[str], output_dir: Path, mode: str) -> list[str]:
    """yt-dlp's progress hook gives the pre-postprocess name. Map to the final files."""
    target_ext = ".mp3" if mode == "mp3" else ".mp4"
    finals: list[str] = []
    seen: set[str] = set()
    for raw in intermediate:
        p = Path(raw)
        candidate = p.with_suffix(target_ext)
        if candidate.exists():
            key = str(candidate.resolve())
            if key not in seen:
                seen.add(key)
                finals.append(str(candidate))
            continue
        # fall back: look in output_dir for a file with same stem
        stem = p.stem
        for f in output_dir.iterdir():
            if f.is_file() and f.stem == stem and f.suffix.lower() == target_ext:
                key = str(f.resolve())
                if key not in seen:
                    seen.add(key)
                    finals.append(str(f))
                break
    return finals


class Handler(BaseHTTPRequestHandler):
    server_version = "YTConverterUI/1.0"

    def log_message(self, fmt, *args):  # noqa: A003 - silence default access log
        # Print to stdout so the .command terminal shows just essentials.
        sys.stdout.write("[web] " + (fmt % args) + "\n")

    def _safe_path(self) -> str:
        return urlparse(self.path).path

    def do_GET(self):  # noqa: N802 - http.server signature
        path = self._safe_path()
        if path == "/" or path == "/index.html":
            body = INDEX_HTML.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return

        if path == "/api/defaults":
            _json_response(
                self,
                HTTPStatus.OK,
                {
                    "default_output_dir": str(default_download_root()),
                    "platform": platform.system(),
                    "presets": folder_presets(),
                    "can_pick_folder": platform.system() == "Darwin",
                    "browsers": _detect_browsers(),
                    "connected_browser": _connected_browser(),
                },
            )
            return

        if path == "/api/pick-folder":
            self._pick_folder()
            return

        if path == "/api/browsers":
            _json_response(
                self,
                HTTPStatus.OK,
                {
                    "browsers": _detect_browsers(),
                    "connected": _connected_browser(),
                },
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
        if path == "/api/inspect":
            self._inspect()
            return
        if path == "/api/download":
            self._start_download()
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
        browser = (body.get("browser") or "").strip().lower()
        if browser not in _BROWSER_PATHS:
            _json_response(self, HTTPStatus.BAD_REQUEST,
                           {"error": "Unknown browser. Use safari/chrome/firefox/brave/edge."})
            return
        if not _browser_cookie_path(browser):
            _json_response(self, HTTPStatus.BAD_REQUEST,
                           {"error": f"{_BROWSER_PATHS[browser][0]} is not installed on this Mac."})
            return
        cfg = _load_config()
        cfg["cookies_browser"] = browser
        _save_config(cfg)
        _json_response(self, HTTPStatus.OK, {"ok": True, "connected": browser})

    def _disconnect_browser(self):
        cfg = _load_config()
        cfg.pop("cookies_browser", None)
        _save_config(cfg)
        _json_response(self, HTTPStatus.OK, {"ok": True})

    def _quit(self):
        _json_response(self, HTTPStatus.OK, {"ok": True, "message": "Shutting down…"})
        # Shutdown in a background thread so this response can finish flushing.
        def _stop():
            time.sleep(0.2)
            # Clean up PID/URL files so the next launch doesn't think we're still alive.
            for name in (".tubedrop.pid", ".tubedrop.url"):
                try:
                    (_repo_root / name).unlink()
                except FileNotFoundError:
                    pass
                except Exception:
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

    def _inspect(self):
        body = _read_json_body(self)
        if body is None:
            _json_response(self, HTTPStatus.BAD_REQUEST, {"error": "Invalid JSON"})
            return
        url = _normalize_url(body.get("url", ""))
        if not URL_RE.match(url):
            _json_response(
                self,
                HTTPStatus.BAD_REQUEST,
                {"error": "Doesn't look like a YouTube URL"},
            )
            return
        try:
            info = _fetch_info(url)
        except yt_dlp.utils.DownloadError as e:
            _json_response(self, HTTPStatus.BAD_GATEWAY, {"error": str(e)})
            return
        except Exception as e:
            _json_response(
                self,
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {"error": f"{type(e).__name__}: {e}"},
            )
            return
        info["normalized_url"] = url
        _json_response(self, HTTPStatus.OK, info)

    def _start_download(self):
        body = _read_json_body(self)
        if body is None:
            _json_response(self, HTTPStatus.BAD_REQUEST, {"error": "Invalid JSON"})
            return
        url = _normalize_url(body.get("url", ""))
        if not URL_RE.match(url):
            _json_response(self, HTTPStatus.BAD_REQUEST, {"error": "Invalid URL"})
            return
        mode = body.get("mode")
        if mode not in ("mp4", "mp3"):
            _json_response(
                self, HTTPStatus.BAD_REQUEST, {"error": "mode must be mp4 or mp3"}
            )
            return
        quality = str(body.get("quality") or "best")
        if not re.match(r"^(best|\d{2,4})$", quality):
            _json_response(self, HTTPStatus.BAD_REQUEST, {"error": "Bad quality"})
            return

        params = {
            "url": url,
            "mode": mode,
            "quality": quality,
            "output_dir": body.get("output_dir") or "",
            "subtitles": bool(body.get("subtitles")),
        }

        job_id = uuid.uuid4().hex
        q: queue.Queue = queue.Queue()
        with _jobs_lock:
            _jobs[job_id] = {"queue": q, "status": "running", "files": []}
        t = threading.Thread(target=_run_job, args=(job_id, params), daemon=True)
        with _jobs_lock:
            _jobs[job_id]["thread"] = t
        t.start()
        _json_response(self, HTTPStatus.OK, {"job_id": job_id})

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

        q: queue.Queue = job["queue"]
        try:
            while True:
                try:
                    msg = q.get(timeout=15)
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
        from urllib.parse import parse_qs

        q = parse_qs(urlparse(self.path).query)
        initial = q.get("initial", [""])[0] or None
        chosen = pick_folder_via_dialog(initial)
        if chosen is None:
            _json_response(self, HTTPStatus.OK, {"cancelled": True})
            return
        _json_response(self, HTTPStatus.OK, {"path": chosen})

    def _reveal_path(self):
        target = urlparse(self.path).query
        from urllib.parse import parse_qs

        q = parse_qs(target)
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
            try:
                s.bind((HOST, port))
            except OSError:
                continue
            return port
    raise RuntimeError("No free port found")


def _preflight() -> list[str]:
    missing = []
    if not shutil.which("ffmpeg"):
        missing.append("ffmpeg")
    return missing


def serve(open_browser: bool = True, port: int | None = None) -> None:
    missing = _preflight()
    if missing:
        print(
            "\033[31;1mMissing required tools:\033[0m " + ", ".join(missing),
            file=sys.stderr,
        )
        print("Run install.command (no Homebrew needed).")
        sys.exit(1)

    chosen = _find_free_port(port or DEFAULT_PORT)
    httpd = ThreadingHTTPServer((HOST, chosen), Handler)
    _httpd_ref.append(httpd)
    url = f"http://{HOST}:{chosen}/"

    pid_file = _repo_root / ".tubedrop.pid"
    url_file = _repo_root / ".tubedrop.url"
    try:
        pid_file.write_text(str(os.getpid()))
        url_file.write_text(url)
    except Exception:
        pass

    print()
    print(f"\033[32;1m  tubedrop ready:\033[0m {url}")
    print(f"\033[2m  Default output: {default_download_root()}\033[0m")
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
            except FileNotFoundError:
                pass


if __name__ == "__main__":
    serve()
