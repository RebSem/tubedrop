#!/bin/bash
# tubedrop — one-click installer for macOS.
# No Homebrew, no sudo, no global installs. Everything stays in the project folder.

set -e

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
REPO_DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
cd "$REPO_DIR"

BIN_DIR="$REPO_DIR/.bin"
VENV_DIR="$REPO_DIR/.venv"
mkdir -p "$BIN_DIR"

CYAN=$'\033[36;1m'; GREEN=$'\033[32;1m'; YELLOW=$'\033[33;1m'; RED=$'\033[31;1m'; RESET=$'\033[0m'
print_step() { echo; echo "${CYAN}▸ $1${RESET}"; }
print_ok()   { echo "${GREEN}  ✓ $1${RESET}"; }
print_warn() { echo "${YELLOW}  ! $1${RESET}"; }
print_err()  { echo "${RED}  ✗ $1${RESET}"; }

clear
cat <<'BANNER'
  ┌──────────────────────────────────────────┐
  │   tubedrop — installer                   │
  │   No Homebrew or admin password needed   │
  └──────────────────────────────────────────┘
BANNER

# ── Step 1: Python ────────────────────────────────────────────────────────
print_step "Looking for Python 3"
if command -v python3 >/dev/null 2>&1; then
  PY_VER="$(python3 -V 2>&1 | awk '{print $2}')"
  print_ok "Python $PY_VER found"
  PYTHON_BIN="$(command -v python3)"
else
  print_warn "Python 3 missing. Triggering Apple's Command Line Tools installer…"
  print_warn "A macOS dialog will appear — click Install, then come back here."
  xcode-select --install 2>/dev/null || true
  until command -v python3 >/dev/null 2>&1; do
    sleep 3
  done
  PYTHON_BIN="$(command -v python3)"
  print_ok "Python 3 ready"
fi

# ── Step 2: Local venv + yt-dlp ──────────────────────────────────────────
print_step "Creating local Python environment (.venv)"
if [ ! -x "$VENV_DIR/bin/python3" ]; then
  "$PYTHON_BIN" -m venv "$VENV_DIR"
  print_ok "Created .venv"
else
  print_ok "Reusing existing .venv"
fi
"$VENV_DIR/bin/python3" -m pip install --quiet --upgrade pip
"$VENV_DIR/bin/python3" -m pip install --quiet --upgrade yt-dlp
print_ok "yt-dlp installed in .venv"

# ── Step 3: ffmpeg (no Homebrew) ─────────────────────────────────────────
print_step "Installing ffmpeg"
FFMPEG_BIN="$BIN_DIR/ffmpeg"
if [ -x "$FFMPEG_BIN" ] && "$FFMPEG_BIN" -version >/dev/null 2>&1; then
  print_ok "ffmpeg already installed"
elif command -v ffmpeg >/dev/null 2>&1; then
  ln -sf "$(command -v ffmpeg)" "$FFMPEG_BIN"
  print_ok "Linked existing ffmpeg ($(command -v ffmpeg))"
else
  echo "  Downloading static ffmpeg binary from evermeet.cx…"
  TMP_ZIP="$BIN_DIR/ffmpeg.zip"
  curl -L --fail --silent --show-error \
    -o "$TMP_ZIP" \
    "https://evermeet.cx/ffmpeg/getrelease/zip" \
    || { print_err "Failed to download ffmpeg. Check your internet connection."; read -p "Press Return…" _; exit 1; }
  unzip -q -o "$TMP_ZIP" -d "$BIN_DIR"
  rm -f "$TMP_ZIP"
  if [ ! -x "$FFMPEG_BIN" ]; then
    FOUND="$(find "$BIN_DIR" -name 'ffmpeg*' -type f 2>/dev/null | head -1)"
    if [ -n "$FOUND" ] && [ "$FOUND" != "$FFMPEG_BIN" ]; then
      mv "$FOUND" "$FFMPEG_BIN"
    fi
  fi
  chmod +x "$FFMPEG_BIN" 2>/dev/null || true
  xattr -dr com.apple.quarantine "$FFMPEG_BIN" 2>/dev/null || true
  if ! "$FFMPEG_BIN" -version >/dev/null 2>&1; then
    print_err "ffmpeg downloaded but won't run."
    read -p "Press Return…" _; exit 1
  fi
  print_ok "ffmpeg installed (no Homebrew used)"
fi

# ── Step 4: Generate Tubedrop.command ────────────────────────────────────
print_step "Creating Tubedrop launcher"
LAUNCHER="$REPO_DIR/Tubedrop.command"
cat > "$LAUNCHER" <<LAUNCHER_EOF
#!/bin/bash
# tubedrop — double-click to launch.
REPO_DIR="$REPO_DIR"
cd "\$REPO_DIR"
export PATH="\$REPO_DIR/.bin:\$PATH"

# If an instance is already running, just open its tab again.
if [ -f "\$REPO_DIR/.tubedrop.pid" ] && kill -0 "\$(cat "\$REPO_DIR/.tubedrop.pid")" 2>/dev/null; then
  if [ -f "\$REPO_DIR/.tubedrop.url" ]; then
    open "\$(cat "\$REPO_DIR/.tubedrop.url")"
  fi
  # Close this Terminal tab — we have nothing else to do.
  osascript -e 'tell application "Terminal" to close (every window whose name contains "Tubedrop")' >/dev/null 2>&1 &
  exit 0
fi

clear
cat <<BANNER
  ┌──────────────────────────────────────────┐
  │  tubedrop — local YouTube downloader     │
  └──────────────────────────────────────────┘

  Browser will open automatically.
  Use the Quit button in the UI to stop.
  (You can hide this window — just don't close it.)

BANNER

"\$REPO_DIR/.venv/bin/python3" -m ytconverter -W
STATUS=\$?

echo
echo "  tubedrop stopped. You can close this window."

# Try to auto-close the Terminal window (best effort, ignored if not Terminal.app).
osascript <<'OSA' >/dev/null 2>&1 &
tell application "Terminal"
  set winList to every window whose name contains "Tubedrop"
  repeat with w in winList
    close w saving no
  end repeat
end tell
OSA
exit \$STATUS
LAUNCHER_EOF
chmod +x "$LAUNCHER"
xattr -d com.apple.quarantine "$LAUNCHER" 2>/dev/null || true
print_ok "Tubedrop.command created"

# ── Step 5: Desktop shortcut ─────────────────────────────────────────────
print_step "Adding Desktop shortcut"
DESKTOP_LINK="$HOME/Desktop/Tubedrop.command"
if [ -e "$DESKTOP_LINK" ] || [ -L "$DESKTOP_LINK" ]; then
  rm -f "$DESKTOP_LINK"
fi
cp "$LAUNCHER" "$DESKTOP_LINK"
chmod +x "$DESKTOP_LINK"
xattr -d com.apple.quarantine "$DESKTOP_LINK" 2>/dev/null || true
print_ok "Desktop ▸ Tubedrop"

# ── Done ─────────────────────────────────────────────────────────────────
echo
echo "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo "${GREEN}  Setup complete.${RESET}"
echo
echo "  Launch any time by double-clicking ${CYAN}Tubedrop${RESET} on your Desktop."
echo "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo

ANSWER=$(osascript -e 'display dialog "tubedrop is ready! Launch it now?" buttons {"Later","Launch"} default button "Launch" with title "tubedrop"' 2>/dev/null || true)
if echo "$ANSWER" | grep -q "Launch"; then
  open "$LAUNCHER"
fi
