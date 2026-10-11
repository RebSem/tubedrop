"""Quality ladder and format choice.

yt-dlp's own ``res`` sort uses the *smallest* frame dimension, which goes
wrong for non-16:9 videos: VK serves 1920×960 streams next to a legacy
progressive "url1080" file that only reports ``height=1080``, and yt-dlp
happily prefers the low-bitrate legacy file. Vertical clips get odd labels
too (1080×1920 shows up as "1920p").

So tubedrop classifies every stream into a familiar quality class
(144p … 4K) and picks formats itself. The same function drives both the
chips the UI shows (with size estimates) and the actual download, so what
you click is what you get.
"""
from __future__ import annotations

from dataclasses import dataclass, field

QUALITY_CLASSES = (144, 240, 360, 480, 720, 1080, 1440, 2160, 4320)

# MP3 targets offered in the UI. "best" is LAME VBR V0 (~245 kbps).
MP3_BITRATES = (320, 256, 192, 128)
MP3_BEST_KBPS = 245

# At the same resolution prefer the most widely playable codec; only reach
# for VP9/AV1 when they are the sole way to get a higher resolution.
_VCODEC_RANK = {"h264": 5, "hevc": 4, None: 3, "vp9": 2, "av1": 1}
_ACODEC_RANK = {"aac": 3, "opus": 2, "mp3": 2, None: 0}


def quality_class(width, height) -> int | None:
    """Map a frame size to 144/240/…/2160, the way YouTube labels quality.

    A frame counts as 1080p if its short side is ~1080 *or* its long side is
    ~1920 — so 1920×960, 1920×800 and 1080×1920 are all "1080p".
    """
    w = width or 0
    h = height or 0
    if not w and not h:
        return None
    if w and h:
        effective = max(min(w, h), max(w, h) * 9 / 16)
    elif h:
        effective = h
    else:
        effective = w * 9 / 16
    for c in reversed(QUALITY_CLASSES):
        if effective >= c * 0.93:
            return c
    return QUALITY_CLASSES[0]


def class_label(c: int | None, fps=None) -> str:
    if not c:
        return "video"
    base = {2160: "4K", 4320: "8K"}.get(c, f"{c}p")
    if fps and 48 <= fps < 100:
        base += str(round(fps))
    return base


def vcodec_family(vcodec) -> str | None:
    v = (vcodec or "").lower()
    if not v or v == "none":
        return None
    if v.startswith(("avc", "h264")):
        return "h264"
    if v.startswith(("hvc", "hev", "h265", "hevc")):
        return "hevc"
    if v.startswith(("vp09", "vp9")):
        return "vp9"
    if v.startswith(("av01", "av1")):
        return "av1"
    return "other"


def acodec_family(acodec) -> str | None:
    a = (acodec or "").lower()
    if not a or a == "none":
        return None
    if a.startswith(("mp4a", "aac")):
        return "aac"
    if a.startswith("opus"):
        return "opus"
    if a.startswith("mp3"):
        return "mp3"
    return "other"


def has_video(f: dict) -> bool:
    # yt-dlp convention: 'none' means absent, None means unknown (assume present).
    if f.get("vcodec") == "none" or f.get("has_drm"):
        return False
    if f.get("ext") == "mhtml" or str(f.get("protocol") or "").startswith("mhtml"):
        return False
    return True


def has_audio(f: dict) -> bool:
    return f.get("acodec") != "none" and not f.get("has_drm") and f.get("ext") != "mhtml"


def is_audio_only(f: dict) -> bool:
    return f.get("vcodec") == "none" and has_audio(f)


def format_size(f: dict, duration=None) -> int | None:
    size = f.get("filesize") or f.get("filesize_approx")
    if size:
        return int(size)
    tbr = f.get("tbr")
    if tbr and duration:
        return int(tbr * 1000 / 8 * duration)
    return None


def _is_drc(f: dict) -> bool:
    text = f"{f.get('format_id') or ''} {f.get('format_note') or ''}".lower()
    return "drc" in text


def _proto_rank(f: dict) -> int:
    proto = str(f.get("protocol") or "")
    if proto in ("https", "http"):
        return 2
    if proto.startswith("m3u8"):
        return 1
    return 0


def _video_key(item):
    idx, f = item
    return (
        quality_class(f.get("width"), f.get("height")) or 0,
        round(f.get("fps") or 0),
        _VCODEC_RANK.get(vcodec_family(f.get("vcodec")), 0),
        0 if (f.get("dynamic_range") or "SDR") != "SDR" else 1,
        _proto_rank(f),
        f.get("tbr") or f.get("vbr") or 0,
        idx,
    )


def _audio_bitrate(f: dict) -> float:
    return f.get("abr") or (f.get("tbr") if f.get("vcodec") == "none" else 0) or 0


def _lang_pref(f: dict) -> int:
    # yt-dlp uses -1 for "nothing special"; None means the extractor didn't say.
    value = f.get("language_preference")
    return -1 if value is None else value


def _audio_key_for_video(item):
    idx, f = item
    br = _audio_bitrate(f)
    return (
        _lang_pref(f),
        0 if _is_drc(f) else 1,
        int(br // 32),
        _ACODEC_RANK.get(acodec_family(f.get("acodec")), 1),
        br,
        idx,
    )


def _audio_key_for_mp3(item):
    idx, f = item
    return (
        _lang_pref(f),
        0 if _is_drc(f) else 1,
        _audio_bitrate(f),
        1 if acodec_family(f.get("acodec")) else 0,
        idx,
    )


@dataclass
class Choice:
    formats: list = field(default_factory=list)
    quality_class: int | None = None
    fps: float | None = None
    vcodec: str | None = None

    @property
    def format_spec(self) -> str:
        return "+".join(f["format_id"] for f in self.formats)

    def size_estimate(self, duration=None) -> int | None:
        if not self.formats:
            return None
        first = format_size(self.formats[0], duration)
        if first is None:
            return None
        rest = sum(format_size(f, duration) or 0 for f in self.formats[1:])
        return first + rest


def choose_video(formats: list, quality: str = "best", can_merge: bool = True) -> Choice | None:
    """Best video (+ separate audio when needed) at or below ``quality``.

    ``formats`` is yt-dlp's list; its order is only used as a final tiebreak.
    """
    videos = [(i, f) for i, f in enumerate(formats) if has_video(f) and f.get("format_id")]
    if not can_merge:
        videos = [v for v in videos if has_audio(v[1])]
    if not videos:
        return None

    target = None if quality in (None, "", "best") else int(quality)
    if target is None:
        eligible = videos
    else:
        eligible = [
            v for v in videos
            if (quality_class(v[1].get("width"), v[1].get("height")) or 0) <= target
        ]
        if not eligible:
            # Nothing that small: take the closest class above the target.
            lowest = min(
                quality_class(v[1].get("width"), v[1].get("height")) or 0 for v in videos
            )
            eligible = [
                v for v in videos
                if (quality_class(v[1].get("width"), v[1].get("height")) or 0) == lowest
            ]

    _, video = max(eligible, key=_video_key)
    chosen = [video]
    if not has_audio(video):
        audios = [(i, f) for i, f in enumerate(formats) if is_audio_only(f) and f.get("format_id")]
        if audios:
            chosen.append(max(audios, key=_audio_key_for_video)[1])
    return Choice(
        formats=chosen,
        quality_class=quality_class(video.get("width"), video.get("height")),
        fps=video.get("fps"),
        vcodec=vcodec_family(video.get("vcodec")),
    )


def choose_audio(formats: list) -> Choice | None:
    """Best audio source for MP3 extraction."""
    audios = [(i, f) for i, f in enumerate(formats) if is_audio_only(f) and f.get("format_id")]
    if audios:
        return Choice(formats=[max(audios, key=_audio_key_for_mp3)[1]])

    muxed = [
        (i, f) for i, f in enumerate(formats)
        if has_video(f) and has_audio(f) and f.get("format_id")
    ]
    if not muxed:
        return None

    # Only muxed streams (some VK videos): the audio track is usually shared
    # between renditions, so avoid downloading a huge 1080p file for it.
    def key(item):
        idx, f = item
        cls = quality_class(f.get("width"), f.get("height")) or 0
        return (
            f.get("abr") or 0,
            1 if cls >= 360 else 0,
            -cls,  # smallest rendition that still carries full audio
            -(f.get("tbr") or 0),
            idx,
        )

    return Choice(formats=[max(muxed, key=key)[1]])


def video_ladder(formats: list, duration=None, can_merge: bool = True,
                 with_sizes: bool = True) -> list[dict]:
    """Quality chips for the UI: "best" first, then each class high → low.

    Pass ``with_sizes=False`` for playlists: the formats belong to the first
    entry only, so its size says nothing about the whole download.
    """
    best = choose_video(formats, "best", can_merge)
    if not best:
        return []
    classes = sorted({
        quality_class(f.get("width"), f.get("height"))
        for f in formats
        if has_video(f) and (can_merge or has_audio(f))
    } - {None}, reverse=True)

    def row(value, choice, label):
        return {
            "value": value,
            "label": label,
            "size_estimate": choice.size_estimate(duration) if with_sizes else None,
            "codec": choice.vcodec,
            "fps": choice.fps,
        }

    out = [row("best", best, class_label(best.quality_class, best.fps))]
    for c in classes:
        choice = choose_video(formats, str(c), can_merge)
        if choice:
            out.append(row(str(c), choice, class_label(c, choice.fps)))
    return out


def audio_ladder(duration=None) -> list[dict]:
    def est(kbps):
        return int(kbps * 1000 / 8 * duration) if duration else None

    out = [{"value": "best", "label": "best", "hint": "VBR", "size_estimate": est(MP3_BEST_KBPS)}]
    for kbps in MP3_BITRATES:
        out.append({"value": str(kbps), "label": str(kbps), "hint": "kbps", "size_estimate": est(kbps)})
    return out


def max_quality_class(formats: list) -> int:
    classes = [
        quality_class(f.get("width"), f.get("height")) or 0
        for f in formats if has_video(f)
    ]
    return max(classes, default=0)


def filename_tag(mode: str, quality: str, choice: Choice | None) -> str:
    """Quality suffix for the output filename, e.g. "1080p50" or "128k".

    Different qualities of one video must not share a filename, otherwise
    yt-dlp treats the old file as "already downloaded" and hands it back.
    """
    if mode == "mp3":
        return "" if quality in (None, "", "best") else f"{quality}k"
    if choice and choice.quality_class:
        return class_label(choice.quality_class, choice.fps)
    return ""


class FormatSelector:
    """Callable for yt-dlp's ``format`` option.

    Picks formats with :func:`choose_video` / :func:`choose_audio`, then lets
    yt-dlp build the (merged) format dict from the chosen IDs so we keep its
    battle-tested merge logic. The quality tag is attached to the selected
    format as ``tubedrop_tag`` so the output template can use it.
    """

    TAG_FIELD = "tubedrop_tag"

    _SPEC_UNSAFE = set("/,[]()+?*")

    def __init__(self, mode: str, quality: str, can_merge: bool):
        self.mode = mode
        self.quality = quality
        self.can_merge = can_merge
        self.ydl = None  # set right after YoutubeDL is constructed
        # yt-dlp selects formats for an entry right before downloading it, so
        # the most recent choice describes the download in progress.
        self.last_choice: Choice | None = None

    def _fallback_spec(self) -> str:
        if self.mode == "mp3":
            return "bestaudio/best"
        return "bv*+ba/b" if self.can_merge else "b"

    def __call__(self, ctx):
        formats = ctx.get("formats") or []
        if self.mode == "mp3":
            choice = choose_audio(formats)
        else:
            choice = choose_video(formats, self.quality, self.can_merge)
        self.last_choice = choice
        spec = choice.format_spec if choice else ""
        if not spec or any(ch in self._SPEC_UNSAFE for f in choice.formats for ch in f["format_id"]):
            spec = self._fallback_spec()
        else:
            # yt-dlp may test-download a chosen format (fresh YouTube HLS) and
            # drop it; fall back to its defaults rather than failing outright.
            spec = f"{spec}/{self._fallback_spec()}"
        tag = filename_tag(self.mode, self.quality, choice)
        for fmt in self.ydl.build_format_selector(spec)(ctx):
            fmt = dict(fmt)
            fmt[self.TAG_FIELD] = tag
            yield fmt
