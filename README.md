<div align="center">

# tubedrop

**Drop a YouTube link. Get the file. That's it.**

A clean web UI for downloading YouTube videos and audio — runs locally on your Mac, no ads, no upload limits, no shady redirects.

![screenshot](docs/screenshot.png)

<sub>Built on top of [kaifcodec/ytconverter](https://github.com/kaifcodec/ytconverter) · UI by [@RebSem](https://github.com/RebSem)</sub>

</div>

---

## Why this exists

Every time I needed to save a YouTube video or rip the audio, the path was the same:
search → land on a sketchy converter site → close 4 pop-ups → realize they cap quality at 360p → try another site → ads with porn → still no file.

It was driving me crazy.

I found a great open-source CLI tool — **[kaifcodec/ytconverter](https://github.com/kaifcodec/ytconverter)** — that does all the heavy lifting via `yt-dlp` and `ffmpeg`. It works perfectly, but it's a terminal tool with prompts.

So I built a small web UI on top of it and packaged everything to install without Terminal, without Homebrew, without an admin password.

---

## Install (Mac, ~1 minute)

**Two clicks. That's it.**

1. **Download** the project: [tubedrop-main.zip](https://github.com/RebSem/tubedrop/archive/refs/heads/main.zip) → unzip wherever (e.g. your Desktop).
2. **Open the folder** and double-click `install.command`.

The installer:
- Uses Python that's already on your Mac (or triggers Apple's free Command Line Tools dialog if missing)
- Downloads a self-contained `ffmpeg` binary into the project folder
- Installs `yt-dlp` into a local virtual environment
- Builds `Tubedrop.app` and puts a shortcut on your Desktop
- Asks if you want to launch right now

**No Homebrew. No `sudo`. No global installs.** Everything stays inside the project folder — to uninstall, just delete the folder.

> **First time:** macOS may say *"install.command can't be opened because it's from an unidentified developer."* Right-click → **Open** → confirm. You only do this once per file.

---

## Run

Double-click **Tubedrop** on your Desktop. The browser opens to the UI.

When you're done — hit the **Quit** button in the top-right of the page. The server shuts down cleanly, no leftover processes.

---

## Features

- **MP4 video** — any available resolution up to 4K
- **MP3 audio** — choose bitrate
- **Real-time progress** — percent, size, speed, ETA
- **Pick folder visually** — quick chips for Downloads / Desktop / Movies / Music, or the native macOS folder picker
- **Subtitles** — toggle on to grab every available language as `.srt`
- **Shorts, playlists, regular videos** — all handled
- **Show in Finder** — one click after a download reveals the file
- **Quit button** — clean shutdown, no orphaned processes

Everything runs on `127.0.0.1`. No remote service, no telemetry, no account.

---

## How it works

Three pieces, all kept inside the project folder:

- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** — installed in `.venv/`, fetches from YouTube
- **[ffmpeg](https://ffmpeg.org/)** — static binary in `.bin/`, merges video+audio and converts to MP3
- **A tiny Python web server** (stdlib only, ~600 lines) — serves the UI, streams progress to the browser over Server-Sent Events

No Electron, no system-wide install, no daemon.

---

## Troubleshooting

**"Setup needed" alert when launching.**
You haven't run `install.command` yet, or it didn't finish. Open the folder and double-click it again.

**Download fails on a specific video.**
YouTube changes things often — keep `yt-dlp` fresh:
```sh
.venv/bin/python3 -m pip install --upgrade yt-dlp
```

**Tubedrop.app won't open ("damaged" or "unverified").**
Right-click the app → **Open** → confirm. Apple's Gatekeeper unblocks it after that.

**Port 8765 already in use.**
The server picks the next free port automatically. The browser opens to whatever URL the app prints.

---

## Credits & license

This project is a UI wrapper built on top of **[kaifcodec/ytconverter](https://github.com/kaifcodec/ytconverter)** — all the actual downloading logic is theirs. If this tool is useful to you, go give them a ⭐.

Heavy lifting also done by [yt-dlp](https://github.com/yt-dlp/yt-dlp) and [ffmpeg](https://ffmpeg.org/).

Licensed under the same terms as the upstream project — see [LICENSE](LICENSE).

---

<sub>Made for personal use. Respect the [YouTube Terms of Service](https://www.youtube.com/static?template=terms) and the rights of content creators.</sub>
