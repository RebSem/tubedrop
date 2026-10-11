<div align="center">

# tubedrop

**Drop a YouTube or VK Video link. Get the file.**

![tubedrop](docs/screenshot.png)

<sub>Built on [kaifcodec/ytconverter](https://github.com/kaifcodec/ytconverter) · ui by [@RebSem](https://github.com/RebSem) · [rebsem.ru](https://rebsem.ru)</sub>

</div>

---

## Why

I just wanted to save a video from YouTube. Every converter site I tried was the same:
sketchy popups, redirects, fake "Download" buttons, hard caps at 360p, and you walk away with nothing.

[**kaifcodec/ytconverter**](https://github.com/kaifcodec/ytconverter) already solved the hard part — `yt-dlp` and `ffmpeg` glued together perfectly. But it's a terminal tool with prompts.

I wrapped it in a small web UI so it's two clicks instead of ten keystrokes.

---

## Install — 2 clicks

1. [**Download the zip**](https://github.com/RebSem/tubedrop/archive/refs/heads/main.zip), unzip wherever you want.
2. Double-click `install.command`.

The installer takes ~30 seconds. It:
- Uses the system Python if it's 3.10 or newer, **otherwise downloads a self-contained Python 3.12 (~30 MB)** so you never have to think about Python versions.
- Drops static `ffmpeg` + `ffprobe` binaries into the project folder (native Apple Silicon builds, checksum-verified). An existing copy is reused only if it actually runs.
- Makes sure a JavaScript runtime is available (YouTube needs one) — reuses `deno` / `node` 22+ if you have them, otherwise downloads the official `deno`.
- Installs `yt-dlp` into a local virtual environment (and repairs that environment if it broke).
- Puts a `Tubedrop` shortcut on your Desktop.

Re-running `install.command` is safe and is the fix for anything that stopped working.

No Homebrew. No `sudo`. No global installs. Everything stays in the project folder — delete the folder to uninstall.

> First time only: macOS may show *"can't be opened — unidentified developer"*. Right-click → **Open** → confirm.

---

## Use

Double-click `Tubedrop` on your Desktop → paste a link → pick a quality → hit `download`.

Supported links:

| Site | Examples |
|---|---|
| YouTube | `youtube.com/watch?v=…`, `youtu.be/…`, `/shorts/…`, playlists |
| VK Video | `vkvideo.ru/video-…`, `vk.com/video…`, `vk.ru/…`, clips (`vk.com/clip…`), embeds (`video_ext.php`), playlists |

You can paste a whole message — tubedrop pulls the link out of the text.

- **Quality chips show what the video really has**, with a size estimate: `4K60`, `1080p50`, `720p`… Vertical clips and wide VK videos (1920×960) are labelled the way the site labels them.
- **H.264 is preferred** at each resolution (plays everywhere, hardware-decoded). Where a site only offers VP9/AV1 (YouTube 1440p/4K) you get that — VLC and IINA play it fine.
- **MP3** comes as VBR V0 by default (or 320/256/192/128 kbps), with title, artist and cover art.
- **Playlists** go into their own subfolder, numbered.
- **Subtitles** (optional): Russian, English and the original language, as `.srt`.
- **Cancel** stops the download and cleans up partial files.
- `yt-dlp` updates itself once a day at launch — YouTube and VK change often.

`Quit` in the top-right of the window cleanly stops the local server.

---

## Connect a browser (HD on YouTube, private VK videos)

Sometimes YouTube hides everything above 360p from anonymous tools or asks you to "confirm you're not a bot", and some VK videos are visible only to signed-in users. When that happens, tubedrop shows a banner or a **connect a browser** button:

<div align="center">
  <img src="docs/hd-modal.png" alt="Connect a browser to unlock HD" width="520">
</div>

Pick the browser you're logged into YouTube / VK with (Safari, Chrome, Firefox, Brave, Edge, Opera, Vivaldi, Chromium). tubedrop tells `yt-dlp` to read that browser's cookies.

- **Cookies never leave your Mac.** They're only sent to the sites they belong to, like your browser does.
- **One-time setup.** Your choice is saved to `.tubedrop.config` and used on every launch.
- **Reversible.** Click the browser chip in the header → **disconnect** to go back to anonymous mode.
- **Safari** needs Terminal to have *Full Disk Access* (System Settings → Privacy & Security). Chrome-based browsers show a Keychain prompt — click *Allow*. If cookies can't be read, tubedrop says so and carries on without them.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Yellow "ffmpeg is missing or broken" notice, or only 360p | Double-click `install.command` again. (A Homebrew upgrade can break a Homebrew ffmpeg; the installer now keeps its own copy.) |
| "No JavaScript runtime" notice, few YouTube qualities | Double-click `install.command` again — it adds `deno`. |
| "The site changed something…" | yt-dlp needs an update; tubedrop does this daily at launch. |
| VK channel pages (`vkvideo.ru/@name`) fail | Known yt-dlp issue — open a specific video or playlist instead. |

---

## Files

```
tubedrop/
├── install.command       ← run once
├── Tubedrop.command      ← created by installer (and on Desktop)
├── README.md
├── docs/
│   ├── screenshot.png
│   └── hd-modal.png
├── tests/                ← python -m unittest discover -s tests -t .
└── ytconverter/          ← Python package
    ├── __main__.py       ← entry point (+ daily yt-dlp update)
    ├── platforms.py      ← which links are accepted
    ├── formats.py        ← quality ladder + format choice
    ├── tools.py          ← finds a working ffmpeg / deno
    ├── errors.py         ← friendly error messages
    ├── updater.py
    └── web/              ← local server + UI
        ├── server.py
        └── ui.py
```

After install, these appear (all gitignored):
- `.venv/` — local Python env with `yt-dlp`
- `.bin/ffmpeg`, `.bin/ffprobe` — bundled ffmpeg binaries
- `.bin/deno` — JavaScript runtime for YouTube (only if you had none)
- `.bin/python/` — bundled Python 3.12 (only when your system Python is too old)
- `.tubedrop.config` — your connected browser
- `.tubedrop.ytdlp-check` — when yt-dlp was last updated
- `.tubedrop.pid` / `.url` — runtime state while the server is up

---

## Credits

- Heavy lifting: [**kaifcodec/ytconverter**](https://github.com/kaifcodec/ytconverter) — go star them.
- Underneath: [yt-dlp](https://github.com/yt-dlp/yt-dlp), [ffmpeg](https://ffmpeg.org/).
- UI & packaging: [@RebSem](https://github.com/RebSem).

Licensed under MIT. See [LICENSE](LICENSE).

---

<sub>For personal use. Respect the [YouTube Terms of Service](https://www.youtube.com/static?template=terms) and the [VK Terms](https://vk.com/terms) — download only what you have the right to save.</sub>
