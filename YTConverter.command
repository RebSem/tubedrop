#!/bin/bash
# tubedrop — double-click to launch the local web UI.

set -e

# Resolve the directory this script lives in (works even via symlink/alias).
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
REPO_DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
cd "$REPO_DIR"

# 1. Prefer the project's own venv (created by install.command).
if [ -x "$REPO_DIR/.venv/bin/python3" ]; then
  PY="$REPO_DIR/.venv/bin/python3"
elif [ -x "$REPO_DIR/.venv-3.14/bin/python3" ]; then
  PY="$REPO_DIR/.venv-3.14/bin/python3"
else
  osascript -e 'display alert "Setup needed" message "Please run install.command first (double-click it in this folder)."'
  exit 1
fi

# 2. Make sure ffmpeg is reachable.
if ! command -v ffmpeg >/dev/null 2>&1; then
  osascript -e 'display alert "ffmpeg not found" message "Run install.command again, or install via Homebrew: brew install ffmpeg"'
  exit 1
fi

# 3. Make sure yt-dlp is importable.
if ! "$PY" -c "import yt_dlp" >/dev/null 2>&1; then
  osascript -e 'display alert "Setup incomplete" message "Run install.command again to set up yt-dlp."'
  exit 1
fi

clear
cat <<BANNER
  ┌──────────────────────────────────────────┐
  │  tubedrop — local YouTube downloader      │
  └──────────────────────────────────────────┘

  Browser will open automatically.
  Close this window or press ⌃C to stop.

BANNER

exec "$PY" -m ytconverter -W
