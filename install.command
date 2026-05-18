#!/bin/bash
# tubedrop — first-time installer for macOS.
# Sets up a local Python environment so YTConverter.command works out of the box.

set -e

# Resolve the directory this script lives in (handles symlinks).
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
REPO_DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
cd "$REPO_DIR"

CYAN=$'\033[36;1m'; GREEN=$'\033[32;1m'; YELLOW=$'\033[33;1m'; RED=$'\033[31;1m'; DIM=$'\033[2m'; RESET=$'\033[0m'

print_step() { echo; echo "${CYAN}▸ $1${RESET}"; }
print_ok()   { echo "${GREEN}  ✓ $1${RESET}"; }
print_warn() { echo "${YELLOW}  ! $1${RESET}"; }
print_err()  { echo "${RED}  ✗ $1${RESET}"; }

clear
cat <<'BANNER'
  ┌──────────────────────────────────────┐
  │    tubedrop — installer for macOS    │
  └──────────────────────────────────────┘
BANNER

# 1. Check Homebrew (we only use it if Python or ffmpeg are missing).
HAVE_BREW=0
if command -v brew >/dev/null 2>&1; then
  HAVE_BREW=1
fi

# 2. Make sure Python 3 is available.
print_step "Checking Python 3"
if command -v python3 >/dev/null 2>&1; then
  PY_VER="$(python3 -V 2>&1 | awk '{print $2}')"
  print_ok "Python $PY_VER found"
else
  print_warn "Python 3 not found"
  if [ "$HAVE_BREW" = "1" ]; then
    echo "  Installing via Homebrew…"
    brew install python
  else
    print_err "Install Python 3 manually from https://www.python.org/downloads/macos/ and re-run."
    echo
    read -p "Press Return to close…" _
    exit 1
  fi
fi

# 3. Make sure ffmpeg is available (yt-dlp needs it for merging/mp3).
print_step "Checking ffmpeg"
if command -v ffmpeg >/dev/null 2>&1; then
  print_ok "ffmpeg found at $(command -v ffmpeg)"
else
  print_warn "ffmpeg not found"
  if [ "$HAVE_BREW" = "1" ]; then
    echo "  Installing via Homebrew…"
    brew install ffmpeg
  else
    print_err "Install Homebrew (https://brew.sh) and then run: brew install ffmpeg"
    echo
    read -p "Press Return to close…" _
    exit 1
  fi
fi

# 4. Create the local virtualenv if missing.
print_step "Setting up local Python environment (.venv)"
if [ ! -x "$REPO_DIR/.venv/bin/python3" ]; then
  python3 -m venv "$REPO_DIR/.venv"
  print_ok "Created .venv"
else
  print_ok "Reusing existing .venv"
fi

PY="$REPO_DIR/.venv/bin/python3"

# 5. Install / update yt-dlp inside the venv.
print_step "Installing yt-dlp"
"$PY" -m pip install --quiet --upgrade pip
"$PY" -m pip install --quiet --upgrade yt-dlp
print_ok "yt-dlp ready"

echo
echo "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo "${GREEN}  All set!${RESET}"
echo
echo "  Double-click ${CYAN}YTConverter.command${RESET} in this folder"
echo "  to launch the app any time."
echo "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo
read -p "Press Return to close this window…" _
