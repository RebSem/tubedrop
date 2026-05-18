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

I found a great open-source CLI tool — **[kaifcodec/ytconverter](https://github.com/kaifcodec/ytconverter)** — that does all the heavy lifting via `yt-dlp` and `ffmpeg`. It works perfectly, but it's a terminal tool. Every download is a series of prompts: paste URL, type number for quality, type path, confirm…

So I built a small web UI on top of it. Now downloading something is:

1. Double-click an icon
2. Paste the link in the browser tab that opens
3. Pick MP4 or MP3
4. Pick a folder (or use one of the chips)
5. Hit **Download**

That's the whole loop. Files land in the folder you picked, nothing leaves your Mac.

---

## Features

- **MP4 video** — choose any available resolution (up to 4K when YouTube serves it)
- **MP3 audio** — choose bitrate, extracted via `ffmpeg`
- **Real-time progress** — percent, size, speed, ETA — like a proper downloader
- **Pick folder visually** — chips for Downloads / Desktop / Movies / Music, or use the native macOS folder picker
- **Subtitles** — toggle on to grab every available language as `.srt`
- **Shorts, playlists, regular videos** — all handled by `yt-dlp` underneath
- **Show in Finder** — one click to reveal the saved file

Everything runs on `127.0.0.1` — there's no remote service, no telemetry, no account. Close the terminal window and the app is gone.

---

## Install (Mac, ~30 seconds)

Requirements: **macOS** and an internet connection.

1. Download this repo:

   ```sh
   git clone https://github.com/RebSem/tubedrop.git ~/Desktop/tubedrop
   ```

   Or click the green **Code → Download ZIP** button on GitHub and unzip it wherever you want (e.g. on your Desktop).

2. Open the folder in Finder and double-click **`install.command`**.

   It checks for Python 3 and `ffmpeg`, installs them via [Homebrew](https://brew.sh) if missing, and sets up an isolated Python environment inside the folder. ~30 seconds.

3. Done. Close the installer window.

> **First time:** macOS may say *"install.command can't be opened because it's from an unidentified developer."* Right-click the file → **Open** → confirm. You only need to do this once per script.

---

## Run

Double-click **`YTConverter.command`** in the project folder.

A Terminal window opens (this is the local server — keep it open while you're using the app) and your browser pops up at `http://127.0.0.1:8765/`.

When you're done: close the Terminal window, or hit `⌃C` inside it.

> Want a shortcut on your Desktop? Right-click `YTConverter.command` → **Make Alias** → drag the alias to your Desktop.

---

## How it works

Three pieces:

- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** — does the actual fetching from YouTube. The best-maintained tool in this space.
- **[ffmpeg](https://ffmpeg.org/)** — merges video+audio streams, converts to MP3.
- **A tiny Python web server** (stdlib only, ~500 lines) — serves the UI, talks to `yt-dlp`, streams progress to the browser over Server-Sent Events.

No Electron, no bundled binary, no system-wide install. Everything lives inside the project folder.

---

## Troubleshooting

**"Setup needed" alert when launching.**
You haven't run `install.command` yet, or it didn't finish. Double-click it again and watch for errors.

**"ffmpeg not found" alert.**
Homebrew may not be in your `PATH`. Open Terminal and run:
```sh
brew install ffmpeg
```

**Download fails on a specific video.**
YouTube changes things often — keep `yt-dlp` fresh:
```sh
.venv/bin/python3 -m pip install --upgrade yt-dlp
```
Run that from inside the project folder.

**Port 8765 already in use.**
The server will pick the next free port automatically and print it in the terminal window. Just use whatever URL it shows.

---

## Credits & license

This project is a UI wrapper built on top of **[kaifcodec/ytconverter](https://github.com/kaifcodec/ytconverter)** — all the actual downloading logic is theirs. If this tool is useful to you, go give them a ⭐.

Heavy lifting also done by [yt-dlp](https://github.com/yt-dlp/yt-dlp) and [ffmpeg](https://ffmpeg.org/).

Licensed under the same terms as the upstream project — see [LICENSE](LICENSE).

---

<sub>Made for personal use. Respect the [YouTube Terms of Service](https://www.youtube.com/static?template=terms) and the rights of content creators.</sub>
