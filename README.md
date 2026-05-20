<div align="center">

# tubedrop

**Drop a YouTube link. Get the file.**

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

The installer takes ~30 seconds. It uses the Python that's already on your Mac, downloads a static `ffmpeg`, installs `yt-dlp` locally, and puts a `Tubedrop` shortcut on your Desktop.

No Homebrew. No `sudo`. No global installs. Everything stays in the project folder — delete the folder to uninstall.

> First time only: macOS may show *"can't be opened — unidentified developer"*. Right-click → **Open** → confirm.

---

## Use

Double-click `Tubedrop` on your Desktop → paste a link → pick a quality → hit `download`.

`Quit` in the top-right of the window cleanly stops the local server.

---

## Files

```
tubedrop/
├── install.command       ← run once
├── Tubedrop.command      ← created by installer (and on Desktop)
├── README.md
├── docs/
│   └── screenshot.png
└── ytconverter/          ← Python package
    ├── __main__.py
    ├── constants.py
    ├── utils/
    └── web/              ← local server + UI
        ├── server.py
        └── ui.py
```

After install, `.venv/` and `.bin/` appear (Python env + ffmpeg). Both gitignored.

---

## Credits

- Heavy lifting: [**kaifcodec/ytconverter**](https://github.com/kaifcodec/ytconverter) — go star them.
- Underneath: [yt-dlp](https://github.com/yt-dlp/yt-dlp), [ffmpeg](https://ffmpeg.org/).
- UI & packaging: [@RebSem](https://github.com/RebSem).

Licensed under MIT. See [LICENSE](LICENSE).

---

<sub>For personal use. Respect the [YouTube Terms of Service](https://www.youtube.com/static?template=terms).</sub>
