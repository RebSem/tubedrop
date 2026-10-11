"""Which sites tubedrop accepts, and how to recognise their links.

We deliberately whitelist YouTube and VK Video instead of passing anything
to yt-dlp: the UI copy, the cookie privacy promise and the quality logic are
all written with these two sites in mind.
"""
from __future__ import annotations

import re
from urllib.parse import parse_qs, urlparse

PLATFORMS = {
    "youtube": {
        "label": "YouTube",
        "hosts": ("youtube.com", "youtu.be", "youtube-nocookie.com"),
    },
    "vk": {
        "label": "VK Video",
        "hosts": ("vk.com", "vk.ru", "vkvideo.ru"),
    },
}

# Pasted text often carries more than the link ("look at this: https://…").
_URL_IN_TEXT = re.compile(r"https?://[^\s<>\"'«»]+", re.IGNORECASE)
_BARE_HOST = re.compile(
    r"(?:^|\s)((?:[a-z0-9-]+\.)*(?:youtube\.com|youtu\.be|youtube-nocookie\.com|vk\.com|vk\.ru|vkvideo\.ru)/[^\s<>\"'«»]*)",
    re.IGNORECASE,
)
_TRAILING_PUNCT = ".,;:!?)]}»"


def extract_url(text: str) -> str:
    """Pull the first link out of free-form text and make it absolute.

    Returns "" when nothing link-like is found.
    """
    text = (text or "").strip()
    if not text:
        return ""
    m = _URL_IN_TEXT.search(text)
    if m:
        url = m.group(0)
    else:
        m = _BARE_HOST.search(text)
        if not m:
            # Single token without a scheme, e.g. "vk.com/video-1_2".
            if " " in text:
                return ""
            url = text
        else:
            url = m.group(1)
        url = "https://" + url.lstrip("/")
    url = url.rstrip(_TRAILING_PUNCT)
    if url.lower().startswith("http://"):
        url = "https://" + url[len("http://"):]
    return normalize_url(url)


def normalize_url(url: str) -> str:
    """Rewrite links yt-dlp can't handle into equivalent ones it can.

    VK's ``video_ext.php`` embed page became a JS app, so yt-dlp can no
    longer read it; the regular ``vk.com/video<oid>_<id>`` page still works.
    """
    if detect_platform(url) != "vk":
        return url
    try:
        parsed = urlparse(url)
    except ValueError:
        return url
    if parsed.path.rstrip("/").lower() == "/video_ext.php":
        query = parse_qs(parsed.query)
        oid = (query.get("oid") or [""])[0]
        vid = (query.get("id") or [""])[0]
        if re.fullmatch(r"-?\d+", oid) and re.fullmatch(r"\d+", vid):
            return f"https://vk.com/video{oid}_{vid}"
    return url


def _host(url: str) -> str:
    try:
        host = urlparse(url).hostname or ""
    except ValueError:
        return ""
    return host.lower().rstrip(".")


def detect_platform(url: str) -> str | None:
    """Return "youtube", "vk" or None for an absolute URL."""
    host = _host(url)
    if not host:
        return None
    for pid, meta in PLATFORMS.items():
        for base in meta["hosts"]:
            if host == base or host.endswith("." + base):
                return pid
    return None


def platform_label(pid: str | None) -> str:
    return PLATFORMS.get(pid or "", {}).get("label", "")
