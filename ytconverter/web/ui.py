"""Single-file HTML/CSS/JS for the tubedrop web UI.

Vanilla JS, no React or build step — keeps the launch instant and
works fully offline once the page is loaded. JetBrains Mono is loaded
from Google Fonts when online and falls back to SF Mono otherwise.
"""

INDEX_HTML = r"""<!doctype html>
<html lang="en" data-theme="light">
<head>
<meta charset="utf-8">
<title>tubedrop · YouTube downloader</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@500;600;700;800&display=swap" rel="stylesheet">
<style>
/* ===========================================================
   tubedrop — redesign
   Juicy & playful + monospace techno-vibe
   =========================================================== */
:root {
  --font-mono: 'JetBrains Mono', ui-monospace, 'SF Mono', Menlo, monospace;
  --font-display: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;

  --accent: #0066FF;
  --accent-strong: #0052D4;
  --accent-soft: rgba(0, 102, 255, 0.10);
  --accent-glow: 0 8px 24px -4px rgba(0, 102, 255, 0.45),
                 0 2px 6px rgba(0, 102, 255, 0.20);

  --bg: #F1F0EC;
  --bg-grad: radial-gradient(circle at 20% 0%, #FFFFFF 0%, #F1F0EC 38%, #E8E6E0 100%);
  --surface: #FFFFFF;
  --surface-2: #FAFAF7;
  --surface-elev: #FFFFFF;
  --border: rgba(15, 15, 20, 0.07);
  --border-strong: rgba(15, 15, 20, 0.12);
  --text: #0A0A0F;
  --text-muted: #5E5E66;
  --text-subtle: #8A8A92;
  --chip-bg: rgba(15, 15, 20, 0.04);
  --chip-bg-hover: rgba(15, 15, 20, 0.07);
  --inset-hi: inset 0 1px 0 rgba(255, 255, 255, 0.7);
  --shadow-sm: 0 1px 2px rgba(15, 15, 20, 0.04);
  --shadow-card: 0 1px 0 rgba(255,255,255,0.6) inset,
                 0 1px 2px rgba(15, 15, 20, 0.04),
                 0 8px 24px -8px rgba(15, 15, 20, 0.10),
                 0 24px 48px -16px rgba(15, 15, 20, 0.10);
  --success: #16A34A;
  --success-bg: #DCFCE7;
  --danger: #DC2626;
  --danger-bg: #FEE2E2;
}

[data-theme="dark"] {
  --bg: #0B0B10;
  --bg-grad: radial-gradient(circle at 20% 0%, #1A1A24 0%, #0E0E14 50%, #07070B 100%);
  --surface: #16161D;
  --surface-2: #1B1B23;
  --surface-elev: #1F1F28;
  --border: rgba(255, 255, 255, 0.07);
  --border-strong: rgba(255, 255, 255, 0.13);
  --text: #F2F2F4;
  --text-muted: #9C9CA6;
  --text-subtle: #6B6B75;
  --chip-bg: rgba(255, 255, 255, 0.05);
  --chip-bg-hover: rgba(255, 255, 255, 0.09);
  --inset-hi: inset 0 1px 0 rgba(255, 255, 255, 0.05);
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.4);
  --shadow-card: 0 1px 0 rgba(255,255,255,0.04) inset,
                 0 1px 2px rgba(0, 0, 0, 0.4),
                 0 8px 24px -8px rgba(0, 0, 0, 0.6),
                 0 24px 48px -16px rgba(0, 0, 0, 0.8);
  --accent: #3D88FF;
  --accent-strong: #1E6FFF;
  --accent-soft: rgba(61, 136, 255, 0.14);
  --accent-glow: 0 8px 24px -4px rgba(61, 136, 255, 0.55),
                 0 2px 6px rgba(61, 136, 255, 0.30);
  --success: #34D399;
  --success-bg: rgba(52, 211, 153, 0.12);
  --danger: #F87171;
  --danger-bg: rgba(248, 113, 113, 0.12);
}

* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  min-height: 100vh;
  background: var(--bg);
  background-image: var(--bg-grad);
  background-attachment: fixed;
  color: var(--text);
  font-family: var(--font-mono);
  font-size: 13px;
  line-height: 1.55;
  font-feature-settings: 'ss01', 'cv11', 'zero';
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  transition: background 0.4s ease;
}
button { font-family: inherit; }
input { font-family: inherit; }
::selection { background: var(--accent-soft); }

/* layout */
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32px 24px 48px;
}
.shell {
  width: 100%;
  max-width: 620px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

/* header */
.hdr { display: flex; align-items: center; gap: 14px; padding: 0 4px; }
.brand { display: flex; align-items: center; gap: 14px; flex: 1; min-width: 0; }
.logo {
  position: relative;
  width: 52px; height: 52px; flex-shrink: 0;
  border-radius: 16px;
  background: linear-gradient(160deg,
    color-mix(in oklab, var(--accent) 100%, white 22%) 0%,
    var(--accent) 50%,
    var(--accent-strong) 100%);
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,0.35),
    inset 0 -8px 14px rgba(0,0,0,0.18),
    0 6px 14px -2px rgba(0, 102, 255, 0.45),
    0 12px 28px -6px rgba(0, 102, 255, 0.25);
  display: grid;
  place-items: center;
  overflow: hidden;
}
.logo::after {
  content: ''; position: absolute; inset: 0;
  border-radius: inherit;
  background: radial-gradient(ellipse at 30% 20%, rgba(255,255,255,0.4) 0%, transparent 55%);
  pointer-events: none;
}
.logo-mark {
  font-family: var(--font-mono);
  font-weight: 700; font-size: 19px; letter-spacing: -0.05em;
  color: white; position: relative; z-index: 1;
  text-shadow: 0 1px 0 rgba(0,0,0,0.15);
}
.wordmark { min-width: 0; }
.wordmark h1 {
  font-family: var(--font-mono); font-weight: 700;
  font-size: 22px; letter-spacing: -0.04em;
  margin: 0; line-height: 1.1; color: var(--text);
}
.wordmark .tagline {
  font-family: var(--font-mono); font-size: 11.5px;
  color: var(--text-muted); margin-top: 4px; letter-spacing: 0.01em;
}
.hdr-actions { display: flex; align-items: center; gap: 8px; }

/* pill / status */
.pill-btn {
  appearance: none; border: 1px solid var(--border-strong);
  background: var(--surface); color: var(--text-muted);
  border-radius: 999px; font-family: var(--font-mono);
  font-size: 11.5px; font-weight: 500; padding: 7px 13px;
  cursor: pointer; display: inline-flex; align-items: center; gap: 6px;
  letter-spacing: 0.02em; transition: all 0.15s ease;
  box-shadow: var(--shadow-sm);
}
.pill-btn:hover { background: var(--surface-2); color: var(--text); }
.pill-btn.danger:hover {
  background: var(--danger-bg); color: var(--danger);
  border-color: color-mix(in oklab, var(--danger) 35%, transparent);
}
.pill-btn svg { width: 12px; height: 12px; }

.status {
  display: inline-flex; align-items: center; gap: 7px;
  padding: 7px 13px 7px 11px;
  background: var(--surface); border: 1px solid var(--border-strong);
  border-radius: 999px; font-family: var(--font-mono);
  font-size: 11.5px; font-weight: 500; color: var(--text-muted);
  box-shadow: var(--shadow-sm);
}
.status-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: var(--success);
  box-shadow: 0 0 0 3px color-mix(in oklab, var(--success) 25%, transparent);
  animation: pulse 2.4s ease-in-out infinite;
}
.status.err .status-dot { background: var(--danger); box-shadow: 0 0 0 3px color-mix(in oklab, var(--danger) 25%, transparent); }
.status.warm .status-dot { background: var(--text-subtle); box-shadow: 0 0 0 3px var(--chip-bg); }
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.55; }
}

/* card */
.card {
  position: relative;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 22px;
  box-shadow: var(--shadow-card);
  overflow: hidden;
}
.card::before {
  content: ''; position: absolute; inset: 0;
  border-radius: inherit; pointer-events: none;
  box-shadow: var(--inset-hi);
}

/* hero */
.hero { padding: 6px; }
.drop-zone {
  position: relative; border-radius: 18px;
  background:
    linear-gradient(180deg, color-mix(in oklab, var(--accent) 4%, var(--surface-2)) 0%, var(--surface-2) 100%);
  border: 1.5px dashed color-mix(in oklab, var(--accent) 30%, var(--border-strong));
  padding: 22px 22px 18px;
  transition: all 0.2s ease;
}
.drop-zone.drag {
  border-color: var(--accent);
  background: var(--accent-soft);
  transform: scale(1.005);
}
.drop-label {
  display: flex; align-items: center; gap: 8px;
  font-family: var(--font-mono); font-size: 10.5px; font-weight: 600;
  letter-spacing: 0.12em; text-transform: uppercase;
  color: var(--text-subtle); margin-bottom: 12px;
}
.drop-label svg { width: 12px; height: 12px; flex-shrink: 0; }
.drop-label .kbd {
  font-family: var(--font-mono); font-size: 10px; padding: 2px 6px;
  background: var(--surface); border: 1px solid var(--border-strong);
  border-radius: 6px; color: var(--text-muted);
  letter-spacing: 0; font-weight: 500;
  box-shadow: 0 1px 0 var(--border-strong);
}
.drop-label .spacer { flex: 1; }
.drop-label .normal {
  color: var(--text-subtle); font-weight: 500;
  text-transform: none; letter-spacing: 0;
}

.url-row { display: flex; align-items: stretch; gap: 10px; }
.url-input-wrap { position: relative; flex: 1; display: flex; align-items: center; }
.url-icon {
  position: absolute; left: 16px;
  color: var(--text-subtle); pointer-events: none;
  display: flex; width: 18px; height: 18px;
}
.url-input {
  width: 100%; appearance: none;
  border: 1px solid var(--border-strong);
  background: var(--surface); border-radius: 14px;
  padding: 14px 16px 14px 44px;
  font-family: var(--font-mono); font-size: 14px;
  color: var(--text); outline: none;
  transition: all 0.15s ease;
  box-shadow: var(--shadow-sm);
}
.url-input::placeholder { color: var(--text-subtle); }
.url-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 4px var(--accent-soft), var(--shadow-sm);
}
.url-clear {
  position: absolute; right: 12px;
  width: 22px; height: 22px; border-radius: 50%;
  border: none; background: var(--chip-bg);
  color: var(--text-muted); cursor: pointer;
  display: grid; place-items: center;
  transition: all 0.15s ease;
}
.url-clear:hover { background: var(--chip-bg-hover); color: var(--text); }
.url-clear svg { width: 11px; height: 11px; }

.fetch-btn {
  appearance: none; border: 1px solid var(--border-strong);
  background: var(--surface); color: var(--text);
  border-radius: 14px; padding: 0 18px;
  font-family: var(--font-mono); font-size: 13px; font-weight: 600;
  cursor: pointer; display: inline-flex; align-items: center; gap: 7px;
  letter-spacing: 0.01em; transition: all 0.15s ease;
  box-shadow: var(--shadow-sm); white-space: nowrap;
}
.fetch-btn:hover { background: var(--surface-2); border-color: var(--text-subtle); }
.fetch-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.fetch-btn svg { width: 13px; height: 13px; }

.drop-hint {
  margin-top: 10px; font-family: var(--font-mono);
  font-size: 11px; color: var(--text-subtle);
  display: flex; align-items: center; gap: 6px;
}
.drop-hint svg { width: 12px; height: 12px; }

/* preview */
.preview {
  margin: 14px 6px 6px; border-radius: 16px;
  background: var(--surface-2); border: 1px solid var(--border);
  overflow: hidden; display: grid;
  grid-template-columns: 168px 1fr; gap: 0;
  animation: fadeUp 0.4s cubic-bezier(.2,.8,.2,1);
}
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}
.preview-thumb {
  position: relative; aspect-ratio: 16/9;
  background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
  overflow: hidden;
}
.preview-thumb img { width: 100%; height: 100%; object-fit: cover; display: block; }
.preview-thumb .play {
  position: absolute; inset: 0; display: grid; place-items: center;
  background: linear-gradient(180deg, rgba(0,0,0,0.05) 30%, rgba(0,0,0,0.45) 100%);
  color: white;
}
.preview-thumb .play svg {
  width: 30px; height: 30px;
  filter: drop-shadow(0 2px 8px rgba(0,0,0,0.5));
}
.preview-thumb .duration {
  position: absolute; bottom: 8px; right: 8px;
  font-family: var(--font-mono); font-size: 10.5px; font-weight: 600;
  padding: 3px 7px; border-radius: 6px;
  background: rgba(0,0,0,0.75); color: white;
  letter-spacing: 0.01em; backdrop-filter: blur(8px);
}
.preview-meta {
  padding: 14px 16px; display: flex; flex-direction: column;
  justify-content: center; min-width: 0;
}
.preview-title {
  font-family: var(--font-display); font-weight: 600;
  font-size: 14px; line-height: 1.35; color: var(--text);
  display: -webkit-box; -webkit-line-clamp: 2;
  -webkit-box-orient: vertical; overflow: hidden;
  letter-spacing: -0.005em;
}
.preview-sub {
  margin-top: 6px; font-family: var(--font-mono);
  font-size: 11px; color: var(--text-muted);
  display: flex; align-items: center; gap: 6px; flex-wrap: wrap;
}
.preview-sub .dot { width: 3px; height: 3px; border-radius: 50%; background: var(--text-subtle); }
.preview-sub .channel { color: var(--text); font-weight: 500; }

/* sections */
.section { padding: 18px 22px; border-top: 1px solid var(--border); }
.section:first-child { border-top: none; }
.section-head {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 12px;
}
.section-label {
  font-family: var(--font-mono); font-size: 10.5px; font-weight: 600;
  letter-spacing: 0.12em; text-transform: uppercase;
  color: var(--text-subtle);
  display: flex; align-items: center; gap: 8px;
}
.section-label .num {
  font-family: var(--font-mono); font-size: 9.5px; font-weight: 600;
  width: 16px; height: 16px;
  display: inline-flex; align-items: center; justify-content: center;
  background: var(--chip-bg); color: var(--text-muted);
  border-radius: 5px; letter-spacing: 0;
}

/* segmented (format) */
.segmented {
  display: grid; grid-template-columns: 1fr 1fr; gap: 6px;
  padding: 5px; background: var(--chip-bg); border-radius: 14px;
}
.seg {
  appearance: none; border: none; background: transparent;
  padding: 11px 14px; border-radius: 10px;
  font-family: var(--font-mono); font-size: 13px; font-weight: 500;
  color: var(--text-muted); cursor: pointer;
  display: inline-flex; align-items: center; justify-content: center; gap: 9px;
  transition: all 0.2s ease; letter-spacing: 0.01em;
}
.seg:hover { color: var(--text); }
.seg.active {
  background: var(--surface); color: var(--text); font-weight: 600;
  box-shadow: 0 1px 0 rgba(255,255,255,0.6) inset,
              0 1px 2px rgba(15,15,20,0.06),
              0 4px 10px -2px rgba(15,15,20,0.10);
}
[data-theme="dark"] .seg.active {
  background: var(--surface-elev);
  box-shadow: 0 1px 0 rgba(255,255,255,0.04) inset,
              0 1px 2px rgba(0,0,0,0.4),
              0 4px 10px -2px rgba(0,0,0,0.5);
}
.seg svg { width: 15px; height: 15px; }
.seg .seg-tag {
  font-family: var(--font-mono); font-size: 9.5px; font-weight: 600;
  padding: 2px 5px; border-radius: 4px;
  background: var(--chip-bg); color: var(--text-subtle);
  letter-spacing: 0.04em;
}
.seg.active .seg-tag { background: var(--accent-soft); color: var(--accent); }

/* quality chips */
.q-rail { display: flex; gap: 6px; flex-wrap: wrap; }
.q-chip {
  appearance: none; border: 1px solid var(--border-strong);
  background: var(--surface); color: var(--text-muted);
  padding: 8px 12px; border-radius: 10px;
  font-family: var(--font-mono); font-size: 12px; font-weight: 500;
  cursor: pointer; transition: all 0.15s ease;
  display: inline-flex; align-items: center; gap: 6px;
  letter-spacing: 0.01em; box-shadow: var(--shadow-sm);
}
.q-chip:hover { color: var(--text); border-color: var(--text-subtle); }
.q-chip.active {
  background: var(--accent-soft); color: var(--accent);
  border-color: color-mix(in oklab, var(--accent) 35%, transparent);
  font-weight: 600;
}
.q-chip .q-size {
  font-size: 10px; color: var(--text-subtle); font-weight: 500;
}
.q-chip.active .q-size {
  color: color-mix(in oklab, var(--accent) 70%, var(--text-subtle));
}

/* folder */
.folder-row { display: flex; gap: 8px; align-items: stretch; }
.folder-input-wrap { position: relative; flex: 1; display: flex; align-items: center; }
.f-icon {
  position: absolute; left: 14px;
  color: var(--text-subtle); display: flex;
  width: 16px; height: 16px; pointer-events: none;
}
.folder-input {
  width: 100%; appearance: none;
  border: 1px solid var(--border-strong); background: var(--surface);
  border-radius: 12px; padding: 11px 14px 11px 38px;
  font-family: var(--font-mono); font-size: 12.5px;
  color: var(--text); outline: none;
  transition: all 0.15s ease; box-shadow: var(--shadow-sm);
}
.folder-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 4px var(--accent-soft);
}
.folder-chips { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 10px; }
.f-chip {
  appearance: none; border: 1px solid var(--border-strong);
  background: var(--surface); color: var(--text-muted);
  padding: 7px 11px; border-radius: 999px;
  font-family: var(--font-mono); font-size: 11.5px; font-weight: 500;
  cursor: pointer; transition: all 0.15s ease;
  display: inline-flex; align-items: center; gap: 6px;
  box-shadow: var(--shadow-sm);
}
.f-chip:hover { color: var(--text); border-color: var(--text-subtle); }
.f-chip.active {
  background: var(--accent-soft); color: var(--accent);
  border-color: color-mix(in oklab, var(--accent) 35%, transparent);
  font-weight: 600;
}
.f-chip svg { width: 12px; height: 12px; }

/* toggle */
.toggle-row { display: flex; align-items: center; justify-content: space-between; gap: 16px; }
.toggle-info { display: flex; align-items: center; gap: 12px; min-width: 0; }
.toggle-icon {
  width: 36px; height: 36px; border-radius: 10px;
  background: var(--chip-bg); display: grid; place-items: center;
  color: var(--text-muted); flex-shrink: 0;
}
.toggle-icon svg { width: 17px; height: 17px; }
.toggle-text { min-width: 0; }
.toggle-title {
  font-family: var(--font-display); font-weight: 600;
  font-size: 13.5px; color: var(--text); letter-spacing: -0.005em;
}
.toggle-hint {
  font-family: var(--font-mono); font-size: 11px;
  color: var(--text-muted); margin-top: 2px;
}

.switch { position: relative; width: 44px; height: 26px; flex-shrink: 0; }
.switch input { opacity: 0; width: 0; height: 0; }
.switch .slider {
  position: absolute; inset: 0;
  background: var(--chip-bg-hover); border-radius: 999px;
  cursor: pointer; transition: background 0.25s ease;
  box-shadow: inset 0 1px 2px rgba(0,0,0,0.06);
}
.switch .slider::before {
  content: ''; position: absolute;
  width: 22px; height: 22px; left: 2px; top: 2px;
  background: white; border-radius: 50%;
  box-shadow: 0 1px 2px rgba(0,0,0,0.1), 0 2px 4px rgba(0,0,0,0.12);
  transition: transform 0.25s cubic-bezier(.4,1.6,.5,1);
}
.switch input:checked + .slider { background: var(--accent); }
.switch input:checked + .slider::before { transform: translateX(18px); }

/* CTA */
.cta-wrap { padding: 0 22px 22px; }
.cta {
  width: 100%; appearance: none; border: none;
  border-radius: 16px; padding: 18px 22px;
  background: linear-gradient(180deg,
    color-mix(in oklab, var(--accent) 100%, white 12%) 0%,
    var(--accent) 50%,
    var(--accent-strong) 100%);
  color: white;
  font-family: var(--font-mono); font-size: 15px; font-weight: 700;
  letter-spacing: 0.01em; cursor: pointer;
  display: flex; align-items: center; justify-content: center; gap: 10px;
  position: relative;
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,0.30),
    inset 0 -8px 14px rgba(0,0,0,0.16),
    var(--accent-glow);
  transition: transform 0.08s ease, box-shadow 0.2s ease;
  overflow: hidden;
}
.cta::before {
  content: ''; position: absolute;
  inset: 1px 1px 50% 1px; border-radius: 15px 15px 0 0;
  background: linear-gradient(180deg, rgba(255,255,255,0.20) 0%, rgba(255,255,255,0) 100%);
  pointer-events: none;
}
.cta:hover {
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,0.30),
    inset 0 -8px 14px rgba(0,0,0,0.16),
    0 12px 30px -4px color-mix(in oklab, var(--accent) 60%, transparent),
    0 4px 8px color-mix(in oklab, var(--accent) 25%, transparent);
}
.cta:active { transform: translateY(1px) scale(0.997); }
.cta:disabled {
  background: var(--chip-bg-hover); color: var(--text-subtle);
  cursor: not-allowed; box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
}
.cta:disabled::before { display: none; }
.cta svg { width: 17px; height: 17px; }
.cta .cta-tag {
  font-family: var(--font-mono); font-size: 10.5px; font-weight: 600;
  padding: 3px 7px; background: rgba(255,255,255,0.18);
  border-radius: 6px; margin-left: auto; letter-spacing: 0.06em;
}

/* progress */
.progress {
  padding: 22px; background: var(--surface-2);
  border-radius: 16px; border: 1px solid var(--border);
  animation: fadeUp 0.3s ease-out;
}
.progress-head {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 14px;
}
.progress-stage {
  font-family: var(--font-mono); font-size: 11px;
  color: var(--text-muted);
  display: flex; align-items: center; gap: 8px;
  font-weight: 500; letter-spacing: 0.02em;
}
.spinner {
  width: 12px; height: 12px;
  border: 2px solid var(--chip-bg-hover);
  border-top-color: var(--accent); border-radius: 50%;
  animation: spin 0.8s linear infinite;
  flex-shrink: 0;
}
@keyframes spin { to { transform: rotate(360deg); } }
.progress-pct {
  font-family: var(--font-mono); font-size: 22px; font-weight: 700;
  color: var(--text); letter-spacing: -0.02em;
  font-variant-numeric: tabular-nums;
}
.progress-pct .unit {
  font-size: 13px; color: var(--text-muted);
  font-weight: 500; margin-left: 1px;
}
.bar {
  height: 8px; background: var(--chip-bg);
  border-radius: 999px; overflow: hidden; position: relative;
  box-shadow: inset 0 1px 2px rgba(0,0,0,0.05);
}
.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent), color-mix(in oklab, var(--accent) 70%, #34d158));
  border-radius: 999px; transition: width 0.3s ease-out;
  box-shadow: 0 0 12px color-mix(in oklab, var(--accent) 50%, transparent);
  position: relative;
}
.bar-fill::after {
  content: ''; position: absolute; inset: 0;
  background: linear-gradient(90deg, transparent 30%, rgba(255,255,255,0.4) 50%, transparent 70%);
  animation: shimmer 1.6s linear infinite;
  border-radius: inherit;
}
.bar-fill.indeterminate {
  width: 35% !important;
  animation: slide 1.6s ease-in-out infinite;
}
@keyframes shimmer {
  from { transform: translateX(-100%); }
  to { transform: translateX(100%); }
}
@keyframes slide {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(285%); }
}
.progress-stats {
  display: grid; grid-template-columns: repeat(3, 1fr);
  gap: 14px; margin-top: 16px;
}
.p-stat-label {
  font-family: var(--font-mono); font-size: 9.5px; font-weight: 600;
  letter-spacing: 0.10em; text-transform: uppercase;
  color: var(--text-subtle);
}
.p-stat-val {
  font-family: var(--font-mono); font-size: 13.5px; font-weight: 600;
  color: var(--text); margin-top: 3px;
  font-variant-numeric: tabular-nums; letter-spacing: -0.01em;
}

/* success */
.success {
  padding: 22px; background: var(--surface-2);
  border-radius: 16px; border: 1px solid var(--border);
  animation: fadeUp 0.3s ease-out;
}
.success-head {
  display: flex; align-items: center; gap: 12px; margin-bottom: 14px;
}
.success-icon {
  width: 36px; height: 36px; border-radius: 12px;
  background: var(--success-bg); color: var(--success);
  display: grid; place-items: center;
}
.success-icon svg { width: 18px; height: 18px; }
.success-title {
  font-family: var(--font-display); font-weight: 700;
  font-size: 15px; color: var(--text); letter-spacing: -0.01em;
}
.success-sub {
  font-family: var(--font-mono); font-size: 11.5px;
  color: var(--text-muted); margin-top: 1px;
}
.file-row {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px; background: var(--surface);
  border: 1px solid var(--border); border-radius: 12px;
  margin-top: 8px;
}
.file-row:first-of-type { margin-top: 0; }
.fr-icon {
  width: 32px; height: 32px; border-radius: 8px;
  background: var(--accent-soft); color: var(--accent);
  display: grid; place-items: center; flex-shrink: 0;
}
.fr-icon svg { width: 15px; height: 15px; }
.fr-name {
  font-family: var(--font-mono); font-size: 12px;
  color: var(--text); white-space: nowrap; overflow: hidden;
  text-overflow: ellipsis; font-weight: 500;
}
.fr-size {
  font-family: var(--font-mono); font-size: 10.5px;
  color: var(--text-subtle); margin-top: 2px;
}
.fr-meta { flex: 1; min-width: 0; }
.fr-btn {
  appearance: none; border: 1px solid var(--border-strong);
  background: var(--surface); color: var(--text);
  padding: 6px 12px; border-radius: 8px;
  font-family: var(--font-mono); font-size: 11px; font-weight: 600;
  cursor: pointer; transition: all 0.15s ease;
  flex-shrink: 0;
}
.fr-btn:hover { background: var(--surface-2); border-color: var(--text-subtle); }
.success-actions { display: flex; gap: 8px; margin-top: 14px; }
.success-actions .pill-btn { flex: 1; justify-content: center; }

/* error */
.error {
  padding: 14px 18px; background: var(--danger-bg);
  color: var(--danger); border-radius: 12px;
  font-family: var(--font-mono); font-size: 12.5px;
  display: flex; align-items: flex-start; gap: 10px;
  margin: 6px;
  border: 1px solid color-mix(in oklab, var(--danger) 30%, transparent);
}
.error svg { width: 16px; height: 16px; flex-shrink: 0; margin-top: 1px; }

/* footer */
.foot {
  margin-top: 8px; padding: 0 4px;
  display: flex; flex-direction: column;
  align-items: center; gap: 6px;
  font-family: var(--font-mono); font-size: 11px;
  color: var(--text-subtle);
}
.foot a {
  color: var(--text-muted); text-decoration: none; font-weight: 600;
  transition: color 0.15s ease;
  border-bottom: 1px dashed var(--border-strong);
  padding-bottom: 1px;
}
.foot a:hover { color: var(--accent); border-bottom-color: var(--accent); }
.foot .foot-line {
  display: flex; align-items: center; gap: 10px;
  flex-wrap: wrap; justify-content: center;
}
.foot .dot { width: 3px; height: 3px; border-radius: 50%; background: var(--text-subtle); }
.foot-lock { display: inline-flex; align-items: center; gap: 6px; }
.foot-lock svg { width: 11px; height: 11px; }
.foot-link-inline {
  display: inline-flex; align-items: center; gap: 5px;
}

/* theme toggle */
.theme-toggle {
  width: 34px; height: 34px; padding: 0;
  border-radius: 50%; background: var(--surface);
  border: 1px solid var(--border-strong); color: var(--text-muted);
  cursor: pointer; display: grid; place-items: center;
  transition: all 0.2s ease; box-shadow: var(--shadow-sm);
}
.theme-toggle:hover { color: var(--text); background: var(--surface-2); }
.theme-toggle svg { width: 14px; height: 14px; }

/* goodbye */
/* HD-unlock banner inside the quality section */
.hd-banner {
  margin-top: 12px;
  padding: 12px 14px;
  background: color-mix(in oklab, var(--accent) 8%, var(--surface-2));
  border: 1px solid color-mix(in oklab, var(--accent) 28%, var(--border-strong));
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-family: var(--font-mono);
  font-size: 11.5px;
  animation: fadeUp 0.3s ease-out;
}
.hd-banner-icon {
  width: 28px; height: 28px;
  border-radius: 8px;
  background: var(--accent-soft);
  color: var(--accent);
  display: grid; place-items: center;
  flex-shrink: 0;
}
.hd-banner-icon svg { width: 14px; height: 14px; }
.hd-banner-text { flex: 1; min-width: 0; color: var(--text-muted); line-height: 1.45; }
.hd-banner-text strong { color: var(--text); font-weight: 600; }
.hd-banner-btn {
  appearance: none; border: none;
  background: var(--accent); color: white;
  padding: 8px 14px; border-radius: 9px;
  font-family: var(--font-mono); font-size: 11.5px; font-weight: 600;
  cursor: pointer; transition: all 0.15s ease;
  display: inline-flex; align-items: center; gap: 6px;
  flex-shrink: 0;
  box-shadow: 0 1px 2px rgba(0,102,255,0.25);
}
.hd-banner-btn:hover { background: var(--accent-strong); }
.hd-banner-btn svg { width: 12px; height: 12px; }

/* HD-status chip in header */
.hd-chip {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 7px 11px 7px 9px;
  background: color-mix(in oklab, var(--accent) 12%, var(--surface));
  color: var(--accent);
  border: 1px solid color-mix(in oklab, var(--accent) 32%, var(--border-strong));
  border-radius: 999px;
  font-family: var(--font-mono); font-size: 11px; font-weight: 600;
  letter-spacing: 0.02em;
  cursor: pointer;
  transition: all 0.15s ease;
  box-shadow: var(--shadow-sm);
}
.hd-chip:hover { background: color-mix(in oklab, var(--accent) 20%, var(--surface)); }
.hd-chip svg { width: 12px; height: 12px; }

/* Modal */
.modal-backdrop {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.36);
  backdrop-filter: blur(8px);
  display: grid; place-items: center;
  z-index: 50;
  padding: 24px;
  animation: fadeIn 0.18s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
[data-theme="dark"] .modal-backdrop { background: rgba(0,0,0,0.6); }
.modal {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 20px;
  box-shadow: 0 30px 80px -20px rgba(0,0,0,0.4);
  width: 100%;
  max-width: 520px;
  max-height: 90vh;
  overflow-y: auto;
  padding: 28px;
  animation: modalIn 0.22s cubic-bezier(.2,.8,.2,1);
}
@keyframes modalIn {
  from { opacity: 0; transform: translateY(10px) scale(0.98); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}
.modal-head { display: flex; align-items: flex-start; gap: 14px; margin-bottom: 16px; }
.modal-icon {
  width: 44px; height: 44px; border-radius: 12px;
  background: var(--accent-soft); color: var(--accent);
  display: grid; place-items: center; flex-shrink: 0;
}
.modal-icon svg { width: 22px; height: 22px; }
.modal h2 {
  font-family: var(--font-display); font-size: 18px; font-weight: 700;
  margin: 0; line-height: 1.25; letter-spacing: -0.02em;
  color: var(--text);
}
.modal-sub {
  font-family: var(--font-mono); font-size: 11.5px;
  color: var(--text-muted); margin-top: 3px;
}
.modal-body p {
  font-family: var(--font-mono); font-size: 12.5px;
  color: var(--text-muted); line-height: 1.6;
  margin: 0 0 12px;
}
.modal-body p strong { color: var(--text); font-weight: 600; }
.modal-bullet {
  display: flex; gap: 10px; font-family: var(--font-mono);
  font-size: 12px; color: var(--text-muted); padding: 8px 0;
  line-height: 1.5;
}
.modal-bullet svg {
  width: 14px; height: 14px; flex-shrink: 0; margin-top: 2px;
  color: var(--success);
}
.modal-divider {
  height: 1px; background: var(--border); margin: 14px 0;
}
.modal-section-label {
  font-family: var(--font-mono); font-size: 10.5px; font-weight: 600;
  letter-spacing: 0.12em; text-transform: uppercase;
  color: var(--text-subtle);
  margin-bottom: 10px;
}
.browser-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 8px;
}
.browser-btn {
  appearance: none;
  border: 1px solid var(--border-strong);
  background: var(--surface-2);
  padding: 14px 16px;
  border-radius: 12px;
  font-family: var(--font-mono); font-size: 13px; font-weight: 600;
  color: var(--text);
  cursor: pointer;
  transition: all 0.15s ease;
  display: flex; align-items: center; gap: 10px;
  text-align: left;
}
.browser-btn:hover {
  background: var(--surface);
  border-color: color-mix(in oklab, var(--accent) 40%, transparent);
  transform: translateY(-1px);
  box-shadow: 0 4px 10px -2px rgba(15,15,20,0.08);
}
.browser-btn:disabled {
  opacity: 0.4; cursor: not-allowed;
}
.browser-btn .b-emoji {
  font-size: 18px; line-height: 1; flex-shrink: 0;
}
.browser-btn .b-meta { display: flex; flex-direction: column; gap: 1px; }
.browser-btn .b-name { font-size: 13px; }
.browser-btn .b-hint {
  font-size: 10px; font-weight: 500; color: var(--text-subtle);
  letter-spacing: 0.02em;
}
.modal-actions {
  display: flex; gap: 8px; justify-content: flex-end;
  margin-top: 18px;
}
.modal-actions .pill-btn { padding: 9px 16px; }

.goodbye { text-align: center; padding: 80px 20px; }
.goodbye-icon {
  width: 56px; height: 56px; margin: 0 auto 20px;
  border-radius: 50%; background: var(--success-bg);
  color: var(--success); display: grid; place-items: center;
}
.goodbye h2 {
  font-family: var(--font-display); font-size: 18px; font-weight: 700;
  margin: 0 0 8px; letter-spacing: -0.01em;
}
.goodbye p {
  color: var(--text-muted); font-size: 13px; margin: 0;
}

/* responsive */
@media (max-width: 560px) {
  .app { padding: 20px 14px 32px; }
  .preview { grid-template-columns: 1fr; }
  .progress-stats { grid-template-columns: 1fr 1fr; }
  .url-row { flex-direction: column; }
  .folder-row { flex-direction: column; }
  .fetch-btn { padding: 11px 18px; }
}
</style>
</head>
<body>
<div class="app">
  <div class="shell">

    <!-- header -->
    <header class="hdr">
      <div class="brand">
        <div class="logo"><span class="logo-mark">td</span></div>
        <div class="wordmark">
          <h1>tubedrop</h1>
          <div class="tagline">// drop a youtube link · keep it on your mac</div>
        </div>
      </div>
      <div class="hdr-actions">
        <div id="hd-chip-slot"></div>
        <div class="status warm" id="status"><span class="status-dot"></span><span id="status-label">connecting</span></div>
        <button class="theme-toggle" id="theme-toggle" title="Toggle theme" aria-label="Toggle theme"></button>
        <button class="pill-btn danger" id="quit-btn" title="Stop the local server">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><path d="M10 17l-5-5 5-5M15 12H4"/></svg>
          quit
        </button>
      </div>
    </header>

    <!-- card -->
    <div class="card">

      <!-- hero / drop zone -->
      <div class="hero">
        <div class="drop-zone" id="drop-zone">
          <div class="drop-label">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
            youtube url
            <span class="spacer"></span>
            <span class="kbd">⌘V</span>
            <span class="normal">to paste</span>
          </div>

          <div class="url-row">
            <div class="url-input-wrap">
              <span class="url-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
              </span>
              <input
                id="url"
                class="url-input"
                type="text"
                placeholder="https://youtube.com/watch?v=…"
                autocomplete="off"
                autocapitalize="off"
                autocorrect="off"
                spellcheck="false">
              <button class="url-clear" id="url-clear" title="Clear" style="display:none">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
              </button>
            </div>
            <button class="fetch-btn" id="fetch-btn" disabled>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1"/></svg>
              fetch
            </button>
          </div>

          <div class="drop-hint">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v13m0 0-4.5-4.5M12 16l4.5-4.5M5 21h14"/></svg>
            or drop a link anywhere on this window
          </div>
        </div>

        <div id="preview-area"></div>
      </div>

      <!-- format -->
      <div class="section">
        <div class="section-head">
          <div class="section-label"><span class="num">01</span>format</div>
        </div>
        <div class="segmented" id="format-pills">
          <button class="seg active" data-mode="mp4">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="6" width="14" height="12" rx="2"/><path d="m22 8-6 4 6 4V8Z"/></svg>
            video <span class="seg-tag">MP4</span>
          </button>
          <button class="seg" data-mode="mp3">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
            audio <span class="seg-tag">MP3</span>
          </button>
        </div>
      </div>

      <!-- quality -->
      <div class="section">
        <div class="section-head">
          <div class="section-label"><span class="num">02</span><span id="q-label">video quality</span></div>
        </div>
        <div class="q-rail" id="q-rail"></div>
        <div id="hd-banner-slot"></div>
      </div>

      <!-- folder -->
      <div class="section">
        <div class="section-head">
          <div class="section-label"><span class="num">03</span>save to folder</div>
        </div>
        <div class="folder-row">
          <div class="folder-input-wrap">
            <span class="f-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5a2 2 0 0 1 2-2h3.5L12 5h6a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V5Z"/></svg>
            </span>
            <input id="output" class="folder-input" type="text" spellcheck="false">
          </div>
          <button class="fetch-btn" id="browse-btn">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 20a2 2 0 0 1-1.78-2.91l1.85-3.95A2 2 0 0 1 7.87 12H22l-2.42 5.84A2 2 0 0 1 17.7 20H6Z"/><path d="M2 12V5a2 2 0 0 1 2-2h3.5L10 5h6a2 2 0 0 1 2 2v3"/></svg>
            browse
          </button>
        </div>
        <div class="folder-chips" id="folder-chips"></div>
      </div>

      <!-- subtitles -->
      <div class="section">
        <div class="toggle-row">
          <div class="toggle-info">
            <div class="toggle-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="M7 14h3M14 14h3M7 11h4M13 11h4"/></svg>
            </div>
            <div class="toggle-text">
              <div class="toggle-title">Download subtitles</div>
              <div class="toggle-hint">all available languages · .srt</div>
            </div>
          </div>
          <label class="switch">
            <input type="checkbox" id="subs">
            <span class="slider"></span>
          </label>
        </div>
      </div>

      <!-- progress / success area -->
      <div id="progress-area"></div>

      <!-- CTA -->
      <div class="cta-wrap" id="cta-wrap">
        <button class="cta" id="download-btn" disabled>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v13m0 0-4.5-4.5M12 16l4.5-4.5M5 21h14"/></svg>
          <span id="cta-text">download video</span>
          <span class="cta-tag" id="cta-tag">MP4</span>
        </button>
      </div>
    </div>

    <!-- footer -->
    <footer class="foot">
      <div class="foot-line">
        <span class="foot-lock">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg>
          local server · files never leave your mac
        </span>
      </div>
      <div class="foot-line">
        <span>built on</span>
        <a href="https://github.com/kaifcodec/ytconverter" target="_blank" rel="noreferrer">kaifcodec/ytconverter</a>
        <span class="dot"></span>
        <span>ui by</span>
        <a href="https://github.com/RebSem/tubedrop" target="_blank" rel="noreferrer">
          <span class="foot-link-inline">
            <svg viewBox="0 0 24 24" fill="currentColor" width="11" height="11"><path d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.58.1.79-.25.79-.55v-2.16c-3.2.69-3.87-1.36-3.87-1.36-.53-1.34-1.29-1.7-1.29-1.7-1.05-.72.08-.71.08-.71 1.17.08 1.78 1.2 1.78 1.2 1.04 1.77 2.72 1.26 3.38.96.11-.75.41-1.26.74-1.55-2.55-.29-5.24-1.28-5.24-5.69 0-1.26.45-2.29 1.18-3.1-.12-.29-.51-1.46.11-3.04 0 0 .97-.31 3.18 1.18.92-.26 1.91-.39 2.89-.39.98 0 1.97.13 2.89.39 2.21-1.49 3.18-1.18 3.18-1.18.63 1.58.23 2.75.11 3.04.74.81 1.18 1.84 1.18 3.1 0 4.42-2.69 5.39-5.26 5.68.42.36.79 1.07.79 2.16v3.2c0 .31.21.66.8.55C20.21 21.38 23.5 17.08 23.5 12 23.5 5.65 18.35.5 12 .5z"/></svg>
            RebSem
          </span>
        </a>
        <span class="dot"></span>
        <a href="https://rebsem.ru" target="_blank" rel="noreferrer">
          <span class="foot-link-inline">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="11" height="11"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/></svg>
            rebsem.ru
          </span>
        </a>
      </div>
    </footer>

  </div>
</div>

<div id="modal-root"></div>

<script>
// ---------- icons used in dynamic markup ----------
const I = {
  play:  '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7L8 5z"/></svg>',
  video: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="6" width="14" height="12" rx="2"/><path d="m22 8-6 4 6 4V8Z"/></svg>',
  music: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>',
  folder:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5a2 2 0 0 1 2-2h3.5L12 5h6a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V5Z"/></svg>',
  alert: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 8v4M12 16h.01"/></svg>',
  check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12 5 5L20 7"/></svg>',
  sparkle:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1"/></svg>',
  sun:   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>',
  moon:  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>',
};

const $ = s => document.querySelector(s);
const state = {
  mode: 'mp4',
  quality: 'best',
  inspected: null,
  defaults: null,
  presets: [],
  browsers: [],          // browsers available on this Mac
  connectedBrowser: null, // currently-configured browser id
  serverOk: false,
  job: null,
  status: 'idle',  // idle | downloading | done
};

const BROWSER_EMOJI = {
  safari: '🧭', chrome: '🌐', firefox: '🦊', brave: '🦁', edge: '🌊',
};

// ---------- theme ----------
function applyTheme(t) {
  document.documentElement.dataset.theme = t;
  $('#theme-toggle').innerHTML = t === 'dark' ? I.sun : I.moon;
  try { localStorage.setItem('tubedrop-theme', t); } catch {}
}
function initTheme() {
  let t = 'light';
  try { t = localStorage.getItem('tubedrop-theme') || 'light'; } catch {}
  applyTheme(t);
}
$('#theme-toggle').addEventListener('click', () => {
  const cur = document.documentElement.dataset.theme || 'light';
  applyTheme(cur === 'dark' ? 'light' : 'dark');
});

// ---------- escape ----------
function escH(s) {
  return String(s ?? '').replace(/[&<>"']/g, c => ({
    '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
  })[c]);
}
function escA(s) { return escH(s); }

// ---------- formatting ----------
function fmtDuration(sec) {
  if (sec == null) return '';
  sec = Math.floor(sec);
  const h = Math.floor(sec / 3600);
  const m = Math.floor((sec % 3600) / 60);
  const s = sec % 60;
  if (h) return `${h}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;
  return `${m}:${String(s).padStart(2,'0')}`;
}
function fmtBytes(n) {
  if (!n && n !== 0) return '–';
  const u = ['B','KB','MB','GB'];
  let i = 0;
  while (n >= 1024 && i < u.length - 1) { n /= 1024; i++; }
  return `${n.toFixed(n >= 10 || i === 0 ? 0 : 1)} ${u[i]}`;
}
function fmtViews(n) {
  if (n == null) return '';
  if (n >= 1e9) return (n/1e9).toFixed(1) + 'B';
  if (n >= 1e6) return (n/1e6).toFixed(1) + 'M';
  if (n >= 1e3) return (n/1e3).toFixed(0) + 'K';
  return String(n);
}
function fmtETA(sec) {
  if (sec == null || sec < 0) return '–';
  sec = Math.floor(sec);
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  if (m === 0) return s + 's';
  return m + 'm ' + String(s).padStart(2,'0') + 's';
}

// ---------- defaults ----------
async function loadDefaults() {
  setStatus('warm', 'connecting');
  try {
    const r = await fetch('/api/defaults');
    if (!r.ok) throw new Error('not ok');
    const data = await r.json();
    state.defaults = data;
    state.presets = data.presets || [];
    state.browsers = data.browsers || [];
    state.connectedBrowser = data.connected_browser || null;
    state.serverOk = true;
    setStatus('ok', 'ready');
    $('#output').value = data.default_output_dir;
    $('#output').placeholder = data.default_output_dir;
    renderFolderChips();
    renderQuality();
    renderHDChip();
  } catch (e) {
    setStatus('err', 'server unreachable');
    setTimeout(loadDefaults, 1500);
  }
}

// ---------- HD-unlock (cookies-from-browser) ----------
function renderHDChip() {
  const slot = $('#hd-chip-slot');
  if (!state.connectedBrowser) { slot.innerHTML = ''; return; }
  const label = state.browsers.find(b => b.id === state.connectedBrowser)?.label
                || state.connectedBrowser;
  slot.innerHTML = `
    <button class="hd-chip" id="hd-chip-btn" title="Disconnect ${escH(label)}">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="4" y="11" width="16" height="10" rx="2"/>
        <path d="M8 11V7a4 4 0 0 1 7-2.6"/>
      </svg>
      hd · ${escH(label.toLowerCase())}
    </button>
  `;
  $('#hd-chip-btn').addEventListener('click', openHDModal);
}

function renderHDBanner() {
  const slot = $('#hd-banner-slot');
  const throttled = state.inspected?.youtube_throttled;
  if (!throttled || state.connectedBrowser) { slot.innerHTML = ''; return; }
  slot.innerHTML = `
    <div class="hd-banner">
      <div class="hd-banner-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="4" y="11" width="16" height="10" rx="2"/>
          <path d="M8 11V7a4 4 0 0 1 8 0v4"/>
        </svg>
      </div>
      <div class="hd-banner-text">
        <strong>YouTube limited this video to 360p</strong> for anonymous requests.
        Connect a browser once to unlock HD on this and future videos.
      </div>
      <button class="hd-banner-btn" id="hd-banner-btn">
        unlock hd
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
          <path d="M5 12h14M13 6l6 6-6 6"/>
        </svg>
      </button>
    </div>
  `;
  $('#hd-banner-btn').addEventListener('click', openHDModal);
}

function openHDModal() {
  const root = $('#modal-root');
  const browsers = state.browsers || [];
  const allBrowsers = ['safari','chrome','firefox','brave','edge'];
  const connected = state.connectedBrowser;

  root.innerHTML = `
    <div class="modal-backdrop" id="modal-backdrop">
      <div class="modal" role="dialog" aria-modal="true">
        <div class="modal-head">
          <div class="modal-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="4" y="11" width="16" height="10" rx="2"/>
              <path d="M8 11V7a4 4 0 0 1 8 0v4"/>
            </svg>
          </div>
          <div>
            <h2>Connect a browser to unlock HD</h2>
            <div class="modal-sub">// one-time setup · remembered between launches</div>
          </div>
        </div>
        <div class="modal-body">
          <p>YouTube serves only 360p to anonymous tools for some videos. Reading your browser's logged-in YouTube cookies lifts that cap and unlocks 720p / 1080p / 4K.</p>
          <div class="modal-bullet">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12 5 5L20 7"/></svg>
            <div>Cookies are read locally by <strong>yt-dlp</strong>. They never leave your Mac.</div>
          </div>
          <div class="modal-bullet">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12 5 5L20 7"/></svg>
            <div>tubedrop talks only to <code>youtube.com</code>. No other site sees your cookies.</div>
          </div>
          <div class="modal-bullet">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12 5 5L20 7"/></svg>
            <div>Disconnect any time — the choice is just one line in <code>.tubedrop.config</code>.</div>
          </div>

          <div class="modal-divider"></div>
          <div class="modal-section-label">${connected ? 'Currently connected' : 'Pick a browser'}</div>
          <div class="browser-grid">
            ${allBrowsers.map(bid => {
              const found = browsers.find(b => b.id === bid);
              const label = found?.label || bid.charAt(0).toUpperCase() + bid.slice(1);
              const installed = !!found;
              const isActive = connected === bid;
              return `
                <button class="browser-btn" data-browser="${bid}"
                  ${!installed ? 'disabled' : ''}
                  style="${isActive ? 'border-color: var(--accent); background: var(--accent-soft);' : ''}">
                  <span class="b-emoji">${BROWSER_EMOJI[bid] || '🌐'}</span>
                  <div class="b-meta">
                    <span class="b-name">${escH(label)}</span>
                    <span class="b-hint">${
                      isActive ? '· connected' :
                      installed ? 'use this browser' : 'not installed'
                    }</span>
                  </div>
                </button>
              `;
            }).join('')}
          </div>

          <div class="modal-actions">
            ${connected ? `<button class="pill-btn danger" id="modal-disconnect">disconnect</button>` : ''}
            <button class="pill-btn" id="modal-close">close</button>
          </div>
        </div>
      </div>
    </div>
  `;

  // wire up
  $('#modal-backdrop').addEventListener('click', (e) => {
    if (e.target.id === 'modal-backdrop') closeHDModal();
  });
  $('#modal-close').addEventListener('click', closeHDModal);
  if (connected) $('#modal-disconnect').addEventListener('click', async () => {
    await fetch('/api/disconnect-browser', { method: 'POST' });
    state.connectedBrowser = null;
    renderHDChip();
    closeHDModal();
    // Re-inspect to refresh the throttled banner / quality list.
    if (urlInput.value.trim()) inspect();
  });
  for (const btn of root.querySelectorAll('.browser-btn:not([disabled])')) {
    btn.addEventListener('click', async () => {
      const browser = btn.dataset.browser;
      btn.disabled = true;
      try {
        const r = await fetch('/api/connect-browser', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ browser }),
        });
        const d = await r.json();
        if (!r.ok) { alert(d.error || 'Failed to connect'); btn.disabled = false; return; }
        state.connectedBrowser = browser;
        renderHDChip();
        closeHDModal();
        if (urlInput.value.trim()) inspect();
      } catch (e) {
        alert('Failed to connect: ' + e.message);
        btn.disabled = false;
      }
    });
  }
  document.addEventListener('keydown', escCloseModal);
}

function closeHDModal() {
  $('#modal-root').innerHTML = '';
  document.removeEventListener('keydown', escCloseModal);
}

function escCloseModal(e) {
  if (e.key === 'Escape') closeHDModal();
}

function setStatus(cls, label) {
  const el = $('#status');
  el.className = 'status ' + (cls === 'ok' ? '' : cls);
  $('#status-label').textContent = label;
}

// ---------- format select ----------
for (const b of document.querySelectorAll('#format-pills .seg')) {
  b.addEventListener('click', () => {
    state.mode = b.dataset.mode;
    for (const x of document.querySelectorAll('#format-pills .seg')) {
      x.classList.toggle('active', x === b);
    }
    $('#q-label').textContent = state.mode === 'mp4' ? 'video quality' : 'audio bitrate';
    state.quality = 'best';
    renderQuality();
    updateCTA();
  });
}

// ---------- quality rail ----------
function renderQuality() {
  const rail = $('#q-rail');
  const opts = state.mode === 'mp4' ? videoQualities() : audioQualities();
  rail.innerHTML = opts.map(o => `
    <button class="q-chip ${state.quality === o.value ? 'active' : ''}" data-q="${escA(o.value)}">
      ${escH(o.label)}
      ${o.size ? `<span class="q-size">${escH(o.size)}</span>` : ''}
    </button>
  `).join('');
  for (const b of rail.querySelectorAll('.q-chip')) {
    b.addEventListener('click', () => {
      state.quality = b.dataset.q;
      for (const x of rail.querySelectorAll('.q-chip')) {
        x.classList.toggle('active', x === b);
      }
    });
  }
}

function videoQualities() {
  // Show only the qualities yt-dlp confirmed are available; fall back to a static list.
  const real = state.inspected?.video_qualities;
  if (real?.length) {
    return real.map(q => ({
      value: q.value,
      label: q.label,
      size: q.size_estimate ? '~' + fmtBytes(q.size_estimate) : (q.value === 'best' ? 'auto' : ''),
    }));
  }
  return [
    { value: 'best', label: 'best', size: 'auto' },
    { value: '2160', label: '4K',    size: '~1.2GB' },
    { value: '1440', label: '1440p', size: '~700MB' },
    { value: '1080', label: '1080p', size: '~280MB' },
    { value: '720',  label: '720p',  size: '~140MB' },
    { value: '480',  label: '480p',  size: '~70MB' },
  ];
}
function audioQualities() {
  const real = state.inspected?.audio_bitrates;
  if (real?.length) {
    return real.map(q => ({
      value: q.value,
      label: q.label,
      size: q.size_estimate ? '~' + fmtBytes(q.size_estimate) : (q.value === 'best' ? 'best' : ''),
    }));
  }
  return [
    { value: 'best', label: 'best', size: 'auto' },
    { value: '320',  label: '320',  size: 'kbps' },
    { value: '256',  label: '256',  size: 'kbps' },
    { value: '192',  label: '192',  size: 'kbps' },
    { value: '128',  label: '128',  size: 'kbps' },
  ];
}

// ---------- folder ----------
function renderFolderChips() {
  const cur = ($('#output').value || '').replace(/\/$/, '');
  $('#folder-chips').innerHTML = state.presets.map(p => `
    <button class="f-chip ${p.path.replace(/\/$/, '') === cur ? 'active' : ''}" data-path="${escA(p.path)}">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5a2 2 0 0 1 2-2h3.5L12 5h6a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V5Z"/></svg>
      ${escH(p.label)}
    </button>
  `).join('');
  for (const b of document.querySelectorAll('#folder-chips .f-chip')) {
    b.addEventListener('click', () => {
      $('#output').value = b.dataset.path;
      markActiveChip();
    });
  }
}
function markActiveChip() {
  const cur = ($('#output').value || '').replace(/\/$/, '');
  for (const b of document.querySelectorAll('#folder-chips .f-chip')) {
    b.classList.toggle('active', b.dataset.path.replace(/\/$/, '') === cur);
  }
}
$('#output').addEventListener('input', markActiveChip);

$('#browse-btn').addEventListener('click', async () => {
  const initial = $('#output').value.trim();
  $('#browse-btn').disabled = true;
  try {
    const r = await fetch('/api/pick-folder?initial=' + encodeURIComponent(initial));
    const d = await r.json();
    if (d.path) {
      $('#output').value = d.path;
      markActiveChip();
    }
  } catch {} finally {
    $('#browse-btn').disabled = false;
  }
});

// ---------- url + drop ----------
const urlInput = $('#url');
const urlClear = $('#url-clear');
const fetchBtn = $('#fetch-btn');

urlInput.addEventListener('input', () => {
  urlClear.style.display = urlInput.value ? 'grid' : 'none';
  fetchBtn.disabled = !urlInput.value.trim() || !state.serverOk;
});
urlInput.addEventListener('keydown', e => {
  if (e.key === 'Enter') { e.preventDefault(); inspect(); }
});
urlInput.addEventListener('paste', () => {
  setTimeout(() => { if (urlInput.value.trim()) inspect(); }, 50);
});
urlClear.addEventListener('click', () => {
  urlInput.value = '';
  urlClear.style.display = 'none';
  fetchBtn.disabled = true;
  state.inspected = null;
  $('#preview-area').innerHTML = '';
  $('#hd-banner-slot').innerHTML = '';
  renderQuality();
  updateCTA();
});

// global ⌘V to focus
window.addEventListener('keydown', e => {
  if ((e.metaKey || e.ctrlKey) && e.key === 'v') {
    if (document.activeElement !== urlInput) urlInput.focus();
  }
});

// global drag/drop on whole window
let dragCount = 0;
const dz = $('#drop-zone');
window.addEventListener('dragenter', e => { e.preventDefault(); dragCount++; dz.classList.add('drag'); });
window.addEventListener('dragleave', e => { dragCount--; if (dragCount <= 0) { dragCount = 0; dz.classList.remove('drag'); } });
window.addEventListener('dragover', e => { e.preventDefault(); });
window.addEventListener('drop', e => {
  e.preventDefault();
  dragCount = 0; dz.classList.remove('drag');
  const txt = (e.dataTransfer?.getData('text/plain') || e.dataTransfer?.getData('text/uri-list') || '').trim();
  if (txt && /youtu/i.test(txt)) {
    urlInput.value = txt;
    urlInput.dispatchEvent(new Event('input'));
    inspect();
  }
});

fetchBtn.addEventListener('click', inspect);

async function inspect() {
  const url = urlInput.value.trim();
  if (!url || !state.serverOk) return;
  fetchBtn.disabled = true;
  const oldHTML = fetchBtn.innerHTML;
  fetchBtn.innerHTML = '<span class="spinner"></span>fetching';
  $('#preview-area').innerHTML = '';
  try {
    const r = await fetch('/api/inspect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
    });
    const d = await r.json();
    if (!r.ok) throw new Error(d.error || 'failed to fetch info');
    state.inspected = d;
    if (d.normalized_url) urlInput.value = d.normalized_url;
    renderPreview(d);
    renderQuality();
    renderHDBanner();
    updateCTA();
  } catch (e) {
    showError(e.message);
    state.inspected = null;
    renderQuality();
    renderHDBanner();
  } finally {
    fetchBtn.disabled = !urlInput.value.trim();
    fetchBtn.innerHTML = oldHTML;
  }
}

function renderPreview(info) {
  if (!info) { $('#preview-area').innerHTML = ''; return; }
  const isPlaylist = info.kind === 'playlist';
  const subParts = [];
  if (info.uploader) subParts.push(`<span class="channel">${escH(info.uploader)}</span>`);
  if (isPlaylist) {
    subParts.push('<span class="dot"></span><span>' + info.count + ' videos</span>');
  } else if (info.view_count != null) {
    subParts.push('<span class="dot"></span><span>' + fmtViews(info.view_count) + ' views</span>');
  }
  $('#preview-area').innerHTML = `
    <div class="preview">
      <div class="preview-thumb">
        ${info.thumbnail ? `<img src="${escA(info.thumbnail)}" alt="" onerror="this.style.display='none'">` : ''}
        <div class="play">${I.play}</div>
        ${info.duration ? `<div class="duration">${fmtDuration(info.duration)}</div>` : ''}
      </div>
      <div class="preview-meta">
        <div class="preview-title">${escH(info.title)}</div>
        <div class="preview-sub">${subParts.join('')}</div>
      </div>
    </div>
  `;
}

// ---------- CTA ----------
function updateCTA() {
  const btn = $('#download-btn');
  const tag = $('#cta-tag');
  const txt = $('#cta-text');
  tag.textContent = state.mode === 'mp4' ? 'MP4' : 'MP3';
  txt.textContent = state.mode === 'mp4' ? 'download video' : 'download audio';
  btn.disabled = !state.inspected || state.status === 'downloading';
}

$('#download-btn').addEventListener('click', startDownload);

async function startDownload() {
  if (!state.inspected) return;
  const params = {
    url: urlInput.value.trim(),
    mode: state.mode,
    quality: state.quality,
    output_dir: $('#output').value.trim() || $('#output').placeholder,
    subtitles: $('#subs').checked,
  };
  state.status = 'downloading';
  setCTABusy(true);
  renderProgress({ stage: 'preparing…' });

  let job;
  try {
    const r = await fetch('/api/download', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    const d = await r.json();
    if (!r.ok) throw new Error(d.error || 'failed to start');
    job = d.job_id;
  } catch (e) {
    showError(e.message);
    state.status = 'idle';
    setCTABusy(false);
    return;
  }

  const es = new EventSource('/api/events/' + job);
  state.job = es;

  let percent = null, stage = 'starting…', stats = {};
  es.onmessage = (evt) => {
    let m; try { m = JSON.parse(evt.data); } catch { return; }
    if (m.event === 'stage') {
      stage = m.message;
      renderProgress({ percent, stage, stats });
    } else if (m.event === 'progress') {
      percent = m.percent;
      stats = m;
      renderProgress({ percent, stage, stats });
    } else if (m.event === 'error') {
      showError(m.message);
    } else if (m.event === 'complete') {
      renderComplete(m);
      state.status = 'done';
    } else if (m.event === 'done') {
      es.close();
      state.job = null;
      setCTABusy(false);
    }
  };
  es.onerror = () => {
    es.close();
    state.job = null;
    setCTABusy(false);
    state.status = 'idle';
  };
}

function setCTABusy(on) {
  const btn = $('#download-btn');
  btn.disabled = on || !state.inspected;
  fetchBtn.disabled = on || !urlInput.value.trim();
  $('#browse-btn').disabled = on;
  if (on) {
    btn.innerHTML = `<span class="spinner" style="border-color:rgba(255,255,255,0.3);border-top-color:white;"></span> downloading… <span class="cta-tag">${state.mode.toUpperCase()}</span>`;
  } else if (state.status !== 'done') {
    btn.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v13m0 0-4.5-4.5M12 16l4.5-4.5M5 21h14"/></svg>
      <span id="cta-text">${state.mode === 'mp4' ? 'download video' : 'download audio'}</span>
      <span class="cta-tag" id="cta-tag">${state.mode === 'mp4' ? 'MP4' : 'MP3'}</span>
    `;
  }
}

function renderProgress({ percent, stage, stats }) {
  const pct = percent != null ? Math.max(0, Math.min(100, percent)) : null;
  $('#progress-area').innerHTML = `
    <div class="section">
      <div class="progress">
        <div class="progress-head">
          <div class="progress-stage"><span class="spinner"></span>${escH(stage || '')}</div>
          <div class="progress-pct">${pct != null ? pct.toFixed(1) : '0.0'}<span class="unit">%</span></div>
        </div>
        <div class="bar">
          <div class="bar-fill ${pct == null ? 'indeterminate' : ''}" style="width:${pct != null ? pct.toFixed(1) : 0}%"></div>
        </div>
        <div class="progress-stats">
          <div>
            <div class="p-stat-label">size</div>
            <div class="p-stat-val">${stats?.downloaded != null ? fmtBytes(stats.downloaded) : '–'} / ${stats?.total ? fmtBytes(stats.total) : '?'}</div>
          </div>
          <div>
            <div class="p-stat-label">speed</div>
            <div class="p-stat-val">${stats?.speed ? fmtBytes(stats.speed) + '/s' : '–'}</div>
          </div>
          <div>
            <div class="p-stat-label">eta</div>
            <div class="p-stat-val">${stats?.eta != null ? fmtETA(stats.eta) : '–'}</div>
          </div>
        </div>
      </div>
    </div>
  `;
}

function renderComplete(msg) {
  const files = msg.files || [];
  const rows = files.length
    ? files.map(f => `
        <div class="file-row">
          <div class="fr-icon">${f.toLowerCase().endsWith('.mp3') ? I.music : I.video}</div>
          <div class="fr-meta">
            <div class="fr-name" title="${escA(f)}">${escH(basename(f))}</div>
            ${msg.sizes?.[f] ? `<div class="fr-size">${fmtBytes(msg.sizes[f])}</div>` : ''}
          </div>
          <button class="fr-btn" data-reveal="${escA(f)}">show in finder</button>
        </div>
      `).join('')
    : `
        <div class="file-row">
          <div class="fr-icon">${I.folder}</div>
          <div class="fr-meta"><div class="fr-name">${escH(msg.output_dir)}</div></div>
          <button class="fr-btn" data-reveal="${escA(msg.output_dir)}">open folder</button>
        </div>`;

  $('#progress-area').innerHTML = `
    <div class="section">
      <div class="success">
        <div class="success-head">
          <div class="success-icon">${I.check}</div>
          <div>
            <div class="success-title">Download complete</div>
            <div class="success-sub">${files.length || 1} file${(files.length || 1) !== 1 ? 's' : ''} saved to your mac</div>
          </div>
        </div>
        ${rows}
        <div class="success-actions">
          <button class="pill-btn" id="reset-btn">${I.sparkle} download another</button>
        </div>
      </div>
    </div>
  `;
  // Hide the CTA — there's a "download another" button inside the success card now.
  $('#cta-wrap').style.display = 'none';

  for (const b of document.querySelectorAll('[data-reveal]')) {
    b.addEventListener('click', () => {
      fetch('/api/reveal?path=' + encodeURIComponent(b.dataset.reveal));
    });
  }
  $('#reset-btn')?.addEventListener('click', resetForm);
}

function resetForm() {
  urlInput.value = '';
  urlClear.style.display = 'none';
  state.inspected = null;
  state.status = 'idle';
  $('#preview-area').innerHTML = '';
  $('#progress-area').innerHTML = '';
  $('#hd-banner-slot').innerHTML = '';
  $('#cta-wrap').style.display = '';
  renderQuality();
  updateCTA();
  urlInput.focus();
}

function basename(p) {
  const m = p.match(/[^/\\]+$/);
  return m ? m[0] : p;
}
function showError(msg) {
  $('#progress-area').innerHTML = `<div class="error">${I.alert}<div>${escH(msg)}</div></div>`;
}

// ---------- quit ----------
$('#quit-btn').addEventListener('click', async () => {
  if (state.job && !confirm('A download is running. Quit anyway?')) return;
  if (!state.job && !confirm('Stop tubedrop?')) return;
  try { await fetch('/api/quit', { method: 'POST' }); } catch {}
  document.body.innerHTML = `
    <div class="app"><div class="shell">
      <div class="goodbye">
        <div class="goodbye-icon">${I.check}</div>
        <h2>tubedrop has quit</h2>
        <p>You can safely close this tab.</p>
      </div>
    </div></div>
  `;
  setTimeout(() => { try { window.close(); } catch {} }, 1200);
});

// ---------- init ----------
initTheme();
renderQuality();
loadDefaults();
</script>
</body>
</html>
"""
