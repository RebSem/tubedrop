#!/bin/bash
# tubedrop — one-click installer for macOS (YouTube & VK Video downloader).
# No Homebrew, no sudo, no global installs. Everything stays in the project folder.
#
# Set TUBEDROP_NONINTERACTIVE=1 for scripted runs: no `clear`, no dialogs and
# no "Press Return" pauses — errors just exit with a non-zero status.

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

NONINTERACTIVE=0
case "${TUBEDROP_NONINTERACTIVE:-}" in
  ""|0) ;;
  *) NONINTERACTIVE=1 ;;
esac

# Stop after a fatal error. When double-clicked, keep the Terminal window open
# so the message can be read; in non-interactive mode just exit non-zero.
pause_and_exit() {
  if [ "$NONINTERACTIVE" != 1 ]; then
    read -r -p "Press Return…" _ || true
  fi
  exit 1
}

# Hardware architecture. `uname -m` says x86_64 when Terminal runs under
# Rosetta, but native arm64 builds run fine there too — so ask the hardware.
ARCH="$(uname -m)"
if [ "$(sysctl -in hw.optional.arm64 2>/dev/null)" = "1" ]; then
  ARCH="arm64"
fi

[ "$NONINTERACTIVE" = 1 ] || clear || true
cat <<'BANNER'
  ┌──────────────────────────────────────────┐
  │   tubedrop — installer                   │
  │   YouTube & VK Video downloader          │
  │   No Homebrew or admin password needed   │
  └──────────────────────────────────────────┘
BANNER

# ── Step 1: Python 3.10+ ─────────────────────────────────────────────────
# yt-dlp dropped support for Python 3.9. We need ≥3.10 — if the system only
# has 3.9 (Apple's), download python-build-standalone and use that.
print_step "Looking for Python 3.10+"

PY_LOCAL_DIR="$BIN_DIR/python"
PY_LOCAL_BIN="$PY_LOCAL_DIR/bin/python3"

py_version_ok() {
  local bin="$1"
  [ -x "$bin" ] || return 1
  # { } group: a broken Python (dyld abort) fails quietly instead of printing
  # bash's "Abort trap: 6" line.
  { "$bin" -; } <<'PYEOF' >/dev/null 2>&1
import sys
sys.exit(0 if sys.version_info >= (3, 10) else 1)
PYEOF
}

PYTHON_BIN=""

# 1. local bundled Python wins
if py_version_ok "$PY_LOCAL_BIN"; then
  PY_VER="$("$PY_LOCAL_BIN" -V 2>&1 | awk '{print $2}')"
  print_ok "Bundled Python $PY_VER (in .bin/python)"
  PYTHON_BIN="$PY_LOCAL_BIN"

# 2. system python3 if it's new enough
elif command -v python3 >/dev/null 2>&1 && py_version_ok "$(command -v python3)"; then
  PYTHON_BIN="$(command -v python3)"
  PY_VER="$("$PYTHON_BIN" -V 2>&1 | awk '{print $2}')"
  print_ok "System Python $PY_VER ($PYTHON_BIN)"

# 3. download python-build-standalone (no Homebrew, no sudo)
else
  SYS_VER="$({ python3 -V; } 2>&1 | awk '/^Python /{print $2}')"
  if [ -n "$SYS_VER" ]; then
    print_warn "System Python $SYS_VER is too old — yt-dlp needs ≥ 3.10"
  else
    print_warn "Python 3 not found"
  fi
  echo "  Downloading a self-contained Python 3.12 (~30 MB)…"

  case "$ARCH" in
    arm64)  PY_TRIPLE="aarch64-apple-darwin" ;;
    x86_64) PY_TRIPLE="x86_64-apple-darwin"  ;;
    *) print_err "Unsupported architecture: $ARCH"; pause_and_exit ;;
  esac

  PY_URL="https://github.com/astral-sh/python-build-standalone/releases/download/20251104/cpython-3.12.12+20251104-${PY_TRIPLE}-install_only.tar.gz"
  TMP_TGZ="$BIN_DIR/python.tar.gz"
  rm -rf "$PY_LOCAL_DIR"
  mkdir -p "$PY_LOCAL_DIR"
  curl -L --fail --silent --show-error -o "$TMP_TGZ" "$PY_URL" \
    || { print_err "Failed to download Python. Check your internet connection."; pause_and_exit; }
  tar -xzf "$TMP_TGZ" -C "$PY_LOCAL_DIR" --strip-components=1
  rm -f "$TMP_TGZ"
  xattr -dr com.apple.quarantine "$PY_LOCAL_DIR" 2>/dev/null || true

  if ! py_version_ok "$PY_LOCAL_BIN"; then
    print_err "Downloaded Python won't run."
    pause_and_exit
  fi
  PYTHON_BIN="$PY_LOCAL_BIN"
  print_ok "Bundled Python $("$PY_LOCAL_BIN" -V 2>&1 | awk '{print $2}') installed locally"
fi

# ── Step 2: Local venv + yt-dlp ──────────────────────────────────────────
print_step "Creating local Python environment (.venv)"

# A venv only links to the Python it was created from. If that Python is gone
# (e.g. Homebrew replaced python@3.x during an upgrade) the venv is dead and
# must be rebuilt. The { } group keeps bash's "Abort trap" noise quiet.
venv_ok() {
  { "$VENV_DIR/bin/python3" -c 'import sys; assert sys.version_info >= (3, 10)'; } >/dev/null 2>&1
}

if [ -d "$VENV_DIR" ] && ! venv_ok; then
  print_warn "Existing .venv is broken (its Python is missing or too old) — recreating it"
  rm -rf "$VENV_DIR"
fi
if [ ! -d "$VENV_DIR" ]; then
  "$PYTHON_BIN" -m venv "$VENV_DIR" \
    || { print_err "Failed to create .venv."; pause_and_exit; }
  print_ok "Created .venv"
else
  print_ok "Reusing existing .venv"
fi
"$VENV_DIR/bin/python3" -m pip install --quiet --upgrade pip \
  || print_warn "Couldn't upgrade pip — continuing with the current version"
# Use the nightly build — YouTube changes things often, the stable release
# usually lags a few days behind on the most recent fixes.
"$VENV_DIR/bin/python3" -m pip install --quiet --upgrade --pre "yt-dlp[default]" \
  || { print_err "Failed to install yt-dlp. Check your internet connection."; pause_and_exit; }
# tubedrop looks at this file's mtime to self-update yt-dlp at most once a day.
date +%s > "$REPO_DIR/.tubedrop.ytdlp-check" || true
print_ok "yt-dlp installed in .venv"

# ── Step 3: ffmpeg + ffprobe (no Homebrew) ───────────────────────────────
# yt-dlp needs ffmpeg to merge separate HD video + audio streams (without it
# YouTube silently falls back to 360p) and to convert to MP3; ffprobe is used
# for probing during post-processing.
#
# Never trust a binary just because it exists: a Homebrew ffmpeg breaks after
# `brew upgrade` (dyld: missing libx265…), and evermeet.cx builds are x86_64
# only, so they won't run on Apple Silicon without Rosetta. Preferred source is
# a self-contained static build in .bin; a working system copy is the fallback.
print_step "Installing ffmpeg + ffprobe"

# Does this binary actually run? The { } group also silences bash's
# "Abort trap: 6" line when a broken binary is killed by dyld.
tool_runs() { { "$1" -version; } >/dev/null 2>&1; }

# First SHA-256 digest in a checksum file ("<hash>  <file name>"), lowercased.
sha256_from_file() { grep -Eo '[0-9A-Fa-f]{64}' "$1" 2>/dev/null | head -1 | tr 'A-F' 'a-f'; }

# verify_sha256 <file> <checksum file>
verify_sha256() {
  local want have
  want="$(sha256_from_file "$2")"
  have="$(shasum -a 256 "$1" 2>/dev/null | awk '{print $1}')"
  [ -n "$want" ] && [ "$want" = "$have" ]
}

# install_from_zip <name> <zip> — unpack into a temp dir inside .bin, then move
# the <name> binary to .bin/<name>. (Called from `if`, so set -e is off in
# here — every step checks its own result.)
install_from_zip() {
  local name="$1" zip="$2" tmp found
  tmp="$(mktemp -d "$BIN_DIR/.unpack-$name.XXXXXX")" || return 1
  if ! unzip -q -o "$zip" -d "$tmp" >/dev/null 2>&1; then
    rm -rf "$tmp"; return 1
  fi
  found="$(find "$tmp" -type f -name "$name" 2>/dev/null | head -1)"
  if [ -z "$found" ]; then
    rm -rf "$tmp"; return 1
  fi
  rm -f "$BIN_DIR/$name"
  if ! mv "$found" "$BIN_DIR/$name"; then
    rm -rf "$tmp"; return 1
  fi
  rm -rf "$tmp"
  chmod +x "$BIN_DIR/$name" || return 1
  xattr -dr com.apple.quarantine "$BIN_DIR/$name" 2>/dev/null || true
}

# download_ffmpeg_tool <ffmpeg|ffprobe> — static build into .bin, verified.
download_ffmpeg_tool() {
  local tool="$1" zip="$BIN_DIR/$1.zip" url final
  rm -f "$zip" "$zip.sha256"
  case "$ARCH" in
    arm64)
      # Native arm64 builds with a .sha256 next to every file. The "latest"
      # URL 307-redirects to a versioned /download/<build>/<tool>.zip, and the
      # checksum lives next to *that* URL — so take it from the same request.
      url="https://ffmpeg.martin-riedl.de/redirect/latest/macos/arm64/release/$tool.zip"
      final="$(curl -L --fail --silent --show-error -o "$zip" -w '%{url_effective}' "$url")" \
        || { rm -f "$zip"; return 1; }
      curl -L --fail --silent --show-error -o "$zip.sha256" "$final.sha256" \
        || { rm -f "$zip" "$zip.sha256"; return 1; }
      if ! verify_sha256 "$zip" "$zip.sha256"; then
        print_warn "$tool checksum mismatch — discarding the download"
        rm -f "$zip" "$zip.sha256"
        return 1
      fi
      rm -f "$zip.sha256"
      ;;
    x86_64)
      case "$tool" in
        ffmpeg) url="https://evermeet.cx/ffmpeg/getrelease/zip" ;;
        *)      url="https://evermeet.cx/ffmpeg/getrelease/$tool/zip" ;;
      esac
      curl -L --fail --silent --show-error -o "$zip" "$url" \
        || { rm -f "$zip"; return 1; }
      ;;
    *)
      return 1
      ;;
  esac
  if ! install_from_zip "$tool" "$zip"; then
    rm -f "$zip"; return 1
  fi
  rm -f "$zip"
  if ! tool_runs "$BIN_DIR/$tool"; then
    rm -f "$BIN_DIR/$tool"; return 1
  fi
}

# link_system_tool <tool> — symlink the first system copy that actually runs
# into .bin and print its path.
link_system_tool() {
  local tool="$1" candidate
  for candidate in "$(command -v "$tool" 2>/dev/null)" "/opt/homebrew/bin/$tool" "/usr/local/bin/$tool"; do
    [ -n "$candidate" ] || continue
    [ "$candidate" = "$BIN_DIR/$tool" ] && continue
    if tool_runs "$candidate"; then
      ln -sf "$candidate" "$BIN_DIR/$tool" || return 1
      echo "$candidate"
      return 0
    fi
  done
  return 1
}

case "$ARCH" in
  arm64)  FFMPEG_SOURCE="ffmpeg.martin-riedl.de, native arm64" ;;
  *)      FFMPEG_SOURCE="evermeet.cx" ;;
esac

rm -rf "$BIN_DIR"/.unpack-* 2>/dev/null || true   # leftovers of an interrupted run
for tool in ffmpeg ffprobe; do
  if tool_runs "$BIN_DIR/$tool"; then
    if [ -L "$BIN_DIR/$tool" ]; then
      print_ok "$tool already installed (→ $(readlink "$BIN_DIR/$tool"))"
    else
      print_ok "$tool already installed"
    fi
    continue
  fi
  # Missing, or doesn't run: `rm -f` also clears a dangling symlink.
  rm -f "$BIN_DIR/$tool"
  echo "  Downloading a self-contained $tool (~30 MB, $FFMPEG_SOURCE)…"
  if download_ffmpeg_tool "$tool"; then
    print_ok "$tool installed (no Homebrew used)"
  elif SYSTEM_TOOL="$(link_system_tool "$tool")"; then
    print_warn "Couldn't download $tool — using the system copy instead ($SYSTEM_TOOL)"
  elif [ "$tool" = ffmpeg ]; then
    print_err "ffmpeg is not available. Check your internet connection and run the installer again."
    echo "  tubedrop needs ffmpeg for HD video (merging video + audio) and for MP3."
    pause_and_exit
  else
    print_warn "ffprobe is not available — downloads still work, some post-processing may be limited"
  fi
done

# ── Step 4: JavaScript runtime (needed for YouTube) ──────────────────────
# yt-dlp needs an external JavaScript runtime to unlock YouTube formats;
# without one YouTube offers far fewer qualities. yt-dlp prefers deno ≥ 2.3.0
# (node ≥ 22 also works). VK Video doesn't need it.
print_step "JavaScript runtime (needed for YouTube)"

# version_ge <have> <want> — dotted numeric compare; "v22.1.0" and
# "2.3.0-rc.1" style suffixes are tolerated.
version_ge() {
  local have="${1#v}" want="$2" i h w
  have="${have%%[!0-9.]*}"
  local IFS=.
  # Intentional word-splitting on dots (only digits and dots are left).
  # shellcheck disable=SC2206
  local -a H=($have) W=($want)
  for i in 0 1 2; do
    h="${H[$i]:-0}"; w="${W[$i]:-0}"
    [ "$((10#$h))" -gt "$((10#$w))" ] && return 0
    [ "$((10#$h))" -lt "$((10#$w))" ] && return 1
  done
  return 0
}

# deno_ok / node_ok <path> — runs and is new enough; sets JS_VER.
JS_VER=""
deno_ok() {
  [ -n "$1" ] || return 1
  # First line looks like: deno 2.6.3 (stable, release, aarch64-apple-darwin)
  JS_VER="$({ "$1" --version; } 2>/dev/null | awk 'NR==1 && $1=="deno" {print $2}')"
  [ -n "$JS_VER" ] && version_ge "$JS_VER" 2.3.0
}
node_ok() {
  [ -n "$1" ] || return 1
  JS_VER="$({ "$1" --version; } 2>/dev/null | head -1)"
  case "$JS_VER" in v[0-9]*) ;; *) return 1 ;; esac
  version_ge "$JS_VER" 22.0.0
}

# download_deno — official release zip into .bin, verified against the
# release's .sha256sum asset.
download_deno() {
  local asset zip="$BIN_DIR/deno.zip" url
  case "$ARCH" in
    arm64)  asset="deno-aarch64-apple-darwin.zip" ;;
    x86_64) asset="deno-x86_64-apple-darwin.zip" ;;
    *) return 1 ;;
  esac
  # Pin "latest" to a concrete release tag first, so the zip and its checksum
  # are guaranteed to come from the same release.
  url="$(curl --silent -o /dev/null -w '%{redirect_url}' \
    "https://github.com/denoland/deno/releases/latest/download/$asset" 2>/dev/null)"
  case "$url" in
    https://github.com/denoland/deno/releases/download/*/"$asset") ;;
    *) url="https://github.com/denoland/deno/releases/latest/download/$asset" ;;
  esac
  rm -f "$zip" "$zip.sha256sum"
  curl -L --fail --silent --show-error -o "$zip" "$url" \
    || { rm -f "$zip"; return 1; }
  curl -L --fail --silent --show-error -o "$zip.sha256sum" "$url.sha256sum" \
    || { rm -f "$zip" "$zip.sha256sum"; return 1; }
  if ! verify_sha256 "$zip" "$zip.sha256sum"; then
    print_warn "deno checksum mismatch — discarding the download"
    rm -f "$zip" "$zip.sha256sum"
    return 1
  fi
  rm -f "$zip.sha256sum"
  if ! install_from_zip deno "$zip"; then
    rm -f "$zip"; return 1
  fi
  rm -f "$zip"
  if ! deno_ok "$BIN_DIR/deno"; then
    rm -f "$BIN_DIR/deno"; return 1
  fi
}

# A dead or too-old runtime in .bin would shadow a good one on PATH — drop it.
deno_ok "$BIN_DIR/deno" || rm -f "$BIN_DIR/deno"
node_ok "$BIN_DIR/node" || rm -f "$BIN_DIR/node"

JS_NAME=""; JS_PATH=""
for candidate in "$BIN_DIR/deno" "$(command -v deno 2>/dev/null)" "/opt/homebrew/bin/deno" "$HOME/.deno/bin/deno"; do
  if deno_ok "$candidate"; then JS_NAME="deno"; JS_PATH="$candidate"; break; fi
done
if [ -z "$JS_NAME" ]; then
  for candidate in "$BIN_DIR/node" "$(command -v node 2>/dev/null)" "/opt/homebrew/bin/node" "/usr/local/bin/node"; do
    if node_ok "$candidate"; then JS_NAME="node"; JS_PATH="$candidate"; break; fi
  done
fi

if [ -n "$JS_NAME" ]; then
  if [ "$JS_PATH" != "$BIN_DIR/$JS_NAME" ]; then
    # Link it into .bin so the launcher finds it even if it's not on PATH there.
    ln -sf "$JS_PATH" "$BIN_DIR/$JS_NAME" 2>/dev/null || true
  elif [ -L "$JS_PATH" ]; then
    JS_PATH="$(readlink "$JS_PATH")"
  fi
  print_ok "$JS_NAME ${JS_VER#v} found ($JS_PATH)"
else
  echo "  Downloading deno (~40 MB, github.com/denoland/deno)…"
  if download_deno; then
    print_ok "deno $JS_VER installed (in .bin/deno)"
  else
    print_warn "No JavaScript runtime available — YouTube may offer fewer qualities; VK works regardless."
    echo "  Run the installer again later to retry."
  fi
fi

# ── Step 5: Generate Tubedrop.command ────────────────────────────────────
print_step "Creating Tubedrop launcher"
LAUNCHER="$REPO_DIR/Tubedrop.command"
cat > "$LAUNCHER" <<LAUNCHER_EOF
#!/bin/bash
# tubedrop — double-click to launch.
REPO_DIR="$REPO_DIR"
cd "\$REPO_DIR" || exit 1
# .bin first (ffmpeg, ffprobe, deno), Homebrew last — Finder-launched shells
# don't always have it on PATH.
export PATH="\$REPO_DIR/.bin:\$PATH:/opt/homebrew/bin:/usr/local/bin"
export PYTHONWARNINGS="ignore"

# If an instance is already running, just open its tab again.
if [ -f "\$REPO_DIR/.tubedrop.pid" ] && kill -0 "\$(cat "\$REPO_DIR/.tubedrop.pid")" 2>/dev/null; then
  if [ -f "\$REPO_DIR/.tubedrop.url" ]; then
    open "\$(cat "\$REPO_DIR/.tubedrop.url")"
  fi
  # Close this Terminal tab — we have nothing else to do.
  osascript -e 'tell application "Terminal" to close (every window whose name contains "Tubedrop")' >/dev/null 2>&1 &
  exit 0
fi

# The Python environment breaks if the Python it was built from disappears
# (e.g. after a Homebrew upgrade). Send the user back to the installer.
if ! { "\$REPO_DIR/.venv/bin/python3" -c 'import yt_dlp'; } >/dev/null 2>&1; then
  echo
  echo "  tubedrop's Python environment is missing or broken."
  echo "  Double-click install.command again to repair it. It's in:"
  echo "    \$REPO_DIR"
  echo
  ANSWER=\$(osascript -e 'display dialog "tubedrop needs a quick repair." & return & return & "Double-click install.command in the tubedrop folder again, then launch tubedrop." buttons {"Show installer", "OK"} default button "Show installer" with title "tubedrop" with icon caution' 2>/dev/null || true)
  if echo "\$ANSWER" | grep -q "Show installer"; then
    open -R "\$REPO_DIR/install.command"
  fi
  exit 1
fi

clear
cat <<BANNER
  ┌──────────────────────────────────────────┐
  │  tubedrop — YouTube & VK downloader      │
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

# ── Step 6: Desktop shortcut ─────────────────────────────────────────────
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

if [ "$NONINTERACTIVE" != 1 ]; then
  ANSWER=$(osascript -e 'display dialog "tubedrop is ready! Launch it now?" buttons {"Later","Launch"} default button "Launch" with title "tubedrop"' 2>/dev/null || true)
  if echo "$ANSWER" | grep -q "Launch"; then
    open "$LAUNCHER"
  fi
fi
