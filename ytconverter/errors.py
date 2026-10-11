"""Turn raw yt-dlp errors into something a person can act on."""
from __future__ import annotations

import re

_ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
_PREFIX = re.compile(r"^(?:ERROR|WARNING):\s*")
_EXTRACTOR_PREFIX = re.compile(r"^\[[\w:.-]+\]\s+(?:[\w@.-]+:\s+)?")
_NOISE = (
    re.compile(r";?\s*please report this issue on\s+https?://\S+.*$", re.I | re.S),
    re.compile(r"\s*Confirm you are on the latest version.*$", re.I | re.S),
    re.compile(r"\s*\(caused by .*\)\s*$", re.I | re.S),
    re.compile(r"\s*Use --cookies-from-browser or --cookies for the authentication\.?.*$", re.I | re.S),
    re.compile(r",?\s*use --username and --password options.*$", re.I | re.S),
    re.compile(r"\s*See\s+https?://github\.com/yt-dlp/yt-dlp/wiki/FAQ\S*.*$", re.I | re.S),
)

# (code, patterns, message, needs_browser)
_RULES: list[tuple[str, tuple[str, ...], str, bool]] = [
    (
        "cookies_permission",
        (r"operation not permitted.*cookies", r"cookies.*operation not permitted",
         r"binarycookies.*(permission|not permitted)", r"permission denied.*cookies"),
        "macOS blocked access to the browser's cookies. Give Terminal \"Full Disk Access\" "
        "(System Settings → Privacy & Security), or connect a different browser.",
        False,
    ),
    (
        "cookies_failed",
        (r"could not find .* cookies database", r"failed to (decrypt|load|read) .*cookie",
         r"cookieloaderror", r"keyring", r"cookies? database is locked", r"unsupported browser"),
        "Couldn't read cookies from the connected browser. Quit the browser and try again, "
        "or connect a different one.",
        False,
    ),
    (
        "age_restricted",
        (r"confirm your age", r"age.?restricted", r"inappropriate for some users"),
        "This video is age-restricted. Connect a browser where you're signed in, then try again.",
        True,
    ),
    (
        "bot_check",
        (r"confirm you.?re not a bot", r"sign in to confirm you.?re not", r"not a robot"),
        "YouTube wants to confirm you're not a bot. Connect a browser where you're signed in "
        "to YouTube, then try again.",
        True,
    ),
    (
        "login_required",
        (r"only available for registered users", r"please log in", r"login required",
         r"private video", r"video is private", r"this video is private",
         r"members.only", r"join this channel", r"access denied to video",
         r"requires? (a )?(login|authentication|subscription)", r"need to log in",
         r"available to (this channel's )?members"),
        "This video needs you to be signed in. Connect a browser where you're logged into "
        "the site, then try again.",
        True,
    ),
    (
        "geo",
        (r"not available (in|from) your (region|country|location)", r"geo.?restrict",
         r"blocked it in your country", r"not made this video available in your"),
        "This video isn't available in your region.",
        False,
    ),
    (
        "rate_limited",
        (r"http error 429", r"too many requests", r"rate.?limit"),
        "The site is rate-limiting requests right now. Wait a few minutes and try again.",
        False,
    ),
    (
        "live",
        (r"live event", r"premieres? in", r"is live now", r"currently live",
         r"live stream.*not (yet )?(supported|finished)"),
        "Live streams and premieres can be downloaded after they finish.",
        False,
    ),
    (
        "drm",
        (r"\bdrm\b",),
        "This video is DRM-protected and can't be downloaded.",
        False,
    ),
    (
        "removed",
        (r"video (is )?unavailable", r"has been removed", r"no longer available",
         r"does not exist", r"has been deleted", r"account .* terminated",
         r"(?<!service )(?<!resource )temporarily unavailable", r"removed from public access"),
        "This video is unavailable — it may have been deleted, blocked or made private.",
        False,
    ),
    (
        "ffmpeg_missing",
        (r"ffmpeg (is )?not (installed|found)", r"ffprobe and ffmpeg not found",
         r"ffmpeg.*(library not loaded|dyld)", r"merging of multiple formats but ffmpeg"),
        "ffmpeg is missing or broken, so video and audio can't be combined. "
        "Double-click install.command again to repair it.",
        False,
    ),
    (
        "no_space",
        (r"no space left on device",),
        "There isn't enough free disk space for this download.",
        False,
    ),
    (
        "write_denied",
        (r"permission denied", r"read-only file system", r"operation not permitted"),
        "tubedrop can't write to the chosen folder. Pick another folder and try again.",
        False,
    ),
    (
        "unsupported",
        (r"unsupported url", r"no suitable extractor", r"is not a valid url"),
        "This link doesn't point to a video tubedrop can download.",
        False,
    ),
    (
        "no_formats",
        (r"requested format is not available", r"no video formats found"),
        "No downloadable formats were found for this video.",
        False,
    ),
    (
        "forbidden",
        (r"http error 403", r"\b403\b.*forbidden"),
        "The site refused the download (HTTP 403). Try again in a minute; if it keeps "
        "happening, connect a browser you're signed in with.",
        True,
    ),
    (
        "extractor_broken",
        (r"please report this issue", r"unable to extract", r"list index out of range",
         r"keyerror", r"typeerror", r"nonetype"),
        "The site changed something and yt-dlp can't read this page yet. tubedrop updates "
        "yt-dlp automatically once a day — try again later.",
        False,
    ),
    (
        "network",
        (r"unable to download (webpage|json|api|video data)", r"timed out", r"connection (reset|refused|aborted)",
         r"nodename nor servname", r"name or service not known", r"network is unreachable",
         r"remote end closed connection", r"\bssl\b", r"urlopen error", r"temporary failure in name resolution",
         r"http error 5\d\d"),
        "Network problem while talking to the site. Check your connection and try again.",
        False,
    ),
]


def clean(message) -> str:
    text = _ANSI.sub("", str(message or "")).strip()
    text = _PREFIX.sub("", text)
    text = _EXTRACTOR_PREFIX.sub("", text)
    for pattern in _NOISE:
        text = pattern.sub("", text)
    return text.strip().rstrip(";").strip()


def explain(message) -> dict:
    """Return ``{"code", "message", "detail", "needs_browser"}``."""
    detail = clean(message)
    # Match against the raw text too: clean() strips hints such as
    # "please report this issue" that tell us yt-dlp itself hit a bug.
    haystack = f"{detail}\n{_ANSI.sub('', str(message or ''))}".lower()
    for code, patterns, friendly, needs_browser in _RULES:
        if any(re.search(p, haystack) for p in patterns):
            return {
                "code": code,
                "message": friendly,
                "detail": detail,
                "needs_browser": needs_browser,
            }
    return {
        "code": "unknown",
        "message": detail or "Something went wrong.",
        "detail": detail,
        "needs_browser": False,
    }
