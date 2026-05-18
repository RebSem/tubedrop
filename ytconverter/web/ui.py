"""Single-file HTML/CSS/JS for the YTConverter web UI."""

INDEX_HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>tubedrop · YouTube downloader</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  :root {
    --bg: #f5f5f7;
    --card: #ffffff;
    --border: #e3e3e8;
    --border-strong: #d2d2d7;
    --text: #1d1d1f;
    --muted: #86868b;
    --subtle: #6e6e73;
    --accent: #0071e3;
    --accent-hover: #0077ed;
    --accent-soft: rgba(0,113,227,0.08);
    --danger: #d93025;
    --danger-bg: #fde7e5;
    --success: #137333;
    --success-bg: #e6f4ea;
    --radius-lg: 14px;
    --radius: 10px;
    --radius-sm: 8px;
    --shadow-card: 0 1px 2px rgba(0,0,0,0.04), 0 8px 24px rgba(0,0,0,0.06);
    --shadow-pop: 0 1px 2px rgba(0,0,0,0.06), 0 12px 32px rgba(0,0,0,0.10);
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; background: var(--bg); color: var(--text); }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Segoe UI", Roboto, sans-serif;
    font-size: 14px;
    line-height: 1.5;
    min-height: 100vh;
    -webkit-font-smoothing: antialiased;
  }
  .wrap {
    max-width: 640px;
    margin: 0 auto;
    padding: 40px 20px 64px;
  }

  /* ---- header ---- */
  header {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 28px;
  }
  .logo {
    width: 44px; height: 44px;
    background: linear-gradient(135deg, #0a84ff 0%, #5e5ce6 100%);
    border-radius: 12px;
    display: grid; place-items: center;
    color: white; font-weight: 700; font-size: 17px;
    letter-spacing: -0.04em;
    box-shadow: 0 4px 12px rgba(10,132,255,0.28), inset 0 1px 0 rgba(255,255,255,0.2);
  }
  .title {
    flex: 1;
  }
  h1 {
    font-size: 22px;
    font-weight: 600;
    margin: 0;
    letter-spacing: -0.02em;
  }
  .sub {
    color: var(--muted);
    font-size: 13px;
    margin-top: 1px;
  }
  .status-dot {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: var(--muted);
    padding: 4px 10px;
    background: white;
    border: 1px solid var(--border);
    border-radius: 999px;
  }
  .status-dot::before {
    content: '';
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #c7c7cc;
    transition: background 0.2s;
  }
  .status-dot.ok::before { background: #30d158; }
  .status-dot.err::before { background: #ff453a; }

  /* ---- card ---- */
  .card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 22px;
    margin-bottom: 14px;
    box-shadow: var(--shadow-card);
  }

  /* ---- form blocks ---- */
  .field { margin-bottom: 18px; }
  .field:last-child { margin-bottom: 0; }
  label, .lbl {
    display: block;
    font-weight: 600;
    font-size: 11px;
    color: var(--subtle);
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
  }

  input[type=text], select {
    width: 100%;
    padding: 11px 14px;
    border: 1px solid var(--border-strong);
    border-radius: var(--radius);
    background: white;
    font-size: 14px;
    font-family: inherit;
    color: var(--text);
    transition: border-color 0.15s, box-shadow 0.15s;
  }
  input[type=text]:focus, select:focus {
    outline: none;
    border-color: var(--accent);
    box-shadow: 0 0 0 3px var(--accent-soft);
  }
  select {
    appearance: none;
    -webkit-appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath fill='none' stroke='%2386868b' stroke-width='1.6' stroke-linecap='round' stroke-linejoin='round' d='M1 1l5 5 5-5'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 14px center;
    padding-right: 36px;
  }

  .url-row { display: flex; gap: 8px; }
  .url-row input { flex: 1; }

  /* ---- buttons ---- */
  .btn {
    padding: 11px 18px;
    background: var(--accent);
    color: white;
    border: none;
    border-radius: var(--radius);
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.15s, transform 0.06s, box-shadow 0.15s;
    font-family: inherit;
    white-space: nowrap;
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }
  .btn:hover { background: var(--accent-hover); }
  .btn:active { transform: scale(0.985); }
  .btn:disabled {
    background: #c7c7cc;
    cursor: not-allowed;
  }
  .btn.ghost {
    background: white;
    color: var(--text);
    border: 1px solid var(--border-strong);
  }
  .btn.ghost:hover { background: #fafafc; border-color: #bcbcc1; }
  .btn.ghost:disabled { background: #f5f5f7; color: var(--muted); }
  .btn.lg {
    width: 100%;
    padding: 14px;
    font-size: 15px;
    font-weight: 600;
    box-shadow: 0 2px 6px rgba(0,113,227,0.25);
  }
  .btn.lg:disabled { box-shadow: none; }

  /* ---- format pills ---- */
  .pill-group {
    display: flex;
    gap: 6px;
    background: #f0f0f3;
    padding: 4px;
    border-radius: 12px;
    width: fit-content;
  }
  .pill {
    padding: 8px 18px;
    border-radius: 9px;
    background: transparent;
    border: none;
    color: var(--subtle);
    cursor: pointer;
    font-size: 13px;
    font-weight: 500;
    transition: all 0.15s;
    font-family: inherit;
  }
  .pill:hover { color: var(--text); }
  .pill.active {
    background: white;
    color: var(--text);
    box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 0 rgba(255,255,255,0.5) inset;
  }

  /* ---- folder chips ---- */
  .chips {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    margin-top: 8px;
  }
  .chip {
    padding: 6px 12px;
    border-radius: 999px;
    background: #f0f0f3;
    border: 1px solid transparent;
    color: var(--subtle);
    cursor: pointer;
    font-size: 12px;
    font-weight: 500;
    font-family: inherit;
    transition: all 0.15s;
    display: inline-flex;
    align-items: center;
    gap: 5px;
  }
  .chip:hover { background: #e8e8ed; color: var(--text); }
  .chip.active {
    background: var(--accent-soft);
    color: var(--accent);
    border-color: rgba(0,113,227,0.2);
  }
  .chip svg { width: 13px; height: 13px; }

  .folder-row { display: flex; gap: 8px; align-items: stretch; }
  .folder-row input { flex: 1; }

  /* ---- subtitles toggle ---- */
  .toggle-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 0 0;
    border-top: 1px solid var(--border);
    margin-top: 14px;
  }
  .toggle-row .label-block { font-size: 13px; }
  .toggle-row .label-title { font-weight: 500; }
  .toggle-row .label-hint { color: var(--muted); font-size: 12px; margin-top: 1px; }
  .switch {
    position: relative;
    width: 42px; height: 24px;
    flex-shrink: 0;
  }
  .switch input { opacity: 0; width: 0; height: 0; }
  .switch .slider {
    position: absolute; inset: 0;
    background: #d2d2d7;
    border-radius: 999px;
    transition: background 0.2s;
    cursor: pointer;
  }
  .switch .slider::before {
    content: '';
    position: absolute;
    width: 20px; height: 20px;
    left: 2px; top: 2px;
    background: white;
    border-radius: 50%;
    box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    transition: transform 0.2s;
  }
  .switch input:checked + .slider { background: #30d158; }
  .switch input:checked + .slider::before { transform: translateX(18px); }

  /* ---- meta preview ---- */
  .meta {
    display: flex;
    gap: 12px;
    align-items: center;
    padding: 12px;
    background: #fafafc;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    margin-top: 12px;
    animation: fadeIn 0.25s ease-out;
  }
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(-4px); }
    to { opacity: 1; transform: translateY(0); }
  }
  .thumb {
    width: 88px;
    height: 50px;
    border-radius: 6px;
    background: #e3e3e8;
    background-size: cover;
    background-position: center;
    flex-shrink: 0;
  }
  .meta-text { flex: 1; min-width: 0; }
  .meta-title {
    font-weight: 500;
    font-size: 13px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .meta-sub {
    color: var(--muted);
    font-size: 12px;
    margin-top: 2px;
  }

  /* ---- progress + status ---- */
  .progress-wrap {
    margin-top: 18px;
    padding: 16px;
    background: #fafafc;
    border-radius: var(--radius);
    border: 1px solid var(--border);
    animation: fadeIn 0.25s ease-out;
  }
  .bar {
    height: 6px;
    background: #e3e3e8;
    border-radius: 999px;
    overflow: hidden;
    position: relative;
  }
  .bar-fill {
    height: 100%;
    width: 0%;
    background: linear-gradient(90deg, var(--accent), #34c759);
    border-radius: 999px;
    transition: width 0.2s ease-out;
  }
  .bar-fill.indeterminate {
    width: 35% !important;
    animation: slide 1.4s linear infinite;
  }
  @keyframes slide {
    0%   { transform: translateX(-100%); }
    100% { transform: translateX(285%); }
  }
  .progress-stats {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    margin-top: 10px;
    font-size: 12px;
    color: var(--muted);
    font-variant-numeric: tabular-nums;
  }
  .progress-stats .stat-label {
    display: block;
    color: var(--muted);
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 2px;
  }
  .progress-stats .stat-val {
    color: var(--text);
    font-weight: 500;
    font-size: 13px;
  }
  .stage {
    color: var(--muted);
    font-size: 12px;
    margin-top: 10px;
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .spinner {
    width: 12px; height: 12px;
    border: 2px solid #d2d2d7;
    border-top-color: var(--accent);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  .error {
    color: var(--danger);
    font-size: 13px;
    background: var(--danger-bg);
    padding: 10px 14px;
    border-radius: var(--radius);
    margin-top: 12px;
    border: 1px solid #f5c6c1;
    animation: fadeIn 0.2s ease-out;
  }
  .success {
    background: var(--success-bg);
    border: 1px solid #c5e1cb;
    border-radius: var(--radius);
    padding: 14px;
    margin-top: 12px;
    animation: fadeIn 0.25s ease-out;
  }
  .success h3 {
    margin: 0 0 8px;
    color: var(--success);
    font-size: 13px;
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .file-list {
    list-style: none;
    padding: 0;
    margin: 0;
  }
  .file-list li {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-top: 1px solid #d4ead9;
    font-size: 12px;
  }
  .file-list li:first-child { border-top: none; }
  .file-list .fname {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    flex: 1;
    margin-right: 12px;
    color: var(--text);
  }
  .link-btn {
    background: white;
    border: 1px solid var(--border-strong);
    color: var(--text);
    cursor: pointer;
    font-size: 12px;
    padding: 5px 12px;
    border-radius: 6px;
    font-family: inherit;
    font-weight: 500;
    transition: all 0.15s;
  }
  .link-btn:hover { background: #fafafc; border-color: #bcbcc1; }

  footer {
    text-align: center;
    color: var(--muted);
    font-size: 11px;
    margin-top: 20px;
  }

  /* ---- icons ---- */
  .icon { width: 14px; height: 14px; flex-shrink: 0; }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div class="logo">td</div>
    <div class="title">
      <h1>tubedrop</h1>
      <div class="sub">Drop a YouTube link · keep it on your Mac.</div>
    </div>
    <div class="status-dot" id="server-status">Connecting…</div>
  </header>

  <div class="card">
    <div class="field">
      <label for="url">YouTube URL</label>
      <div class="url-row">
        <input
          id="url"
          type="text"
          placeholder="Paste a YouTube link…"
          autocomplete="off"
          autocapitalize="off"
          autocorrect="off"
          spellcheck="false"
        >
        <button class="btn ghost" id="fetch-btn">Fetch info</button>
      </div>
      <div id="meta-area"></div>
    </div>

    <div class="field">
      <span class="lbl">Format</span>
      <div class="pill-group" id="format-pills">
        <button class="pill active" data-mode="mp4">
          <svg class="icon" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" style="display:inline-block;vertical-align:-2px;margin-right:4px;">
            <rect x="1.5" y="3" width="13" height="10" rx="1.5"/>
            <path d="M6.5 6.5l3 1.5-3 1.5z" fill="currentColor"/>
          </svg>
          Video (MP4)
        </button>
        <button class="pill" data-mode="mp3">
          <svg class="icon" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" style="display:inline-block;vertical-align:-2px;margin-right:4px;">
            <path d="M6 12V4l6-1.5v8"/>
            <circle cx="4.5" cy="12" r="1.5" fill="currentColor"/>
            <circle cx="10.5" cy="10.5" r="1.5" fill="currentColor"/>
          </svg>
          Audio (MP3)
        </button>
      </div>
    </div>

    <div class="field">
      <label id="quality-label" for="quality">Video quality</label>
      <select id="quality"></select>
    </div>

    <div class="field">
      <label>Save to folder</label>
      <div class="folder-row">
        <input id="output" type="text" placeholder="~/Downloads/YTConverter">
        <button class="btn ghost" id="browse-btn" title="Browse for folder">
          <svg class="icon" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M1.5 4.5h4l1.5 1.5h7.5V12a1 1 0 01-1 1h-12a1 1 0 01-1-1V4.5z"/>
          </svg>
          Browse…
        </button>
      </div>
      <div class="chips" id="folder-chips"></div>
    </div>

    <div class="toggle-row">
      <div class="label-block">
        <div class="label-title">Download subtitles</div>
        <div class="label-hint">All available languages, .srt</div>
      </div>
      <label class="switch">
        <input type="checkbox" id="subs">
        <span class="slider"></span>
      </label>
    </div>

    <div style="margin-top: 20px;">
      <button class="btn lg" id="download-btn" disabled>
        <svg class="icon" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M8 2v9m0 0l-3.5-3.5M8 11l3.5-3.5M2.5 13.5h11"/>
        </svg>
        Download
      </button>
    </div>

    <div id="progress-area"></div>
  </div>

  <footer>
    Local server · files never leave your Mac<br>
    <span style="opacity:0.7">Built on
      <a href="https://github.com/kaifcodec/ytconverter" target="_blank" style="color:inherit;">kaifcodec/ytconverter</a>
      · UI by <a href="https://github.com/RebSem" target="_blank" style="color:inherit;">RebSem</a>
    </span>
  </footer>
</div>

<script>
const $ = sel => document.querySelector(sel);
const state = {
  mode: 'mp4',
  inspected: null,
  job: null,
  defaults: null,
  serverOk: false,
};

async function loadDefaults() {
  try {
    const r = await fetch('/api/defaults');
    if (!r.ok) throw new Error('not ok');
    const data = await r.json();
    state.defaults = data;
    state.serverOk = true;
    setServerStatus('ok', 'Ready');
    $('#output').value = data.default_output_dir;
    $('#output').placeholder = data.default_output_dir;
    renderChips(data.presets || [], data.default_output_dir);
    if (!data.can_pick_folder) {
      $('#browse-btn').style.display = 'none';
    }
    $('#download-btn').disabled = false;
  } catch (e) {
    setServerStatus('err', 'Server unreachable');
    setTimeout(loadDefaults, 1500);
  }
}

function setServerStatus(cls, text) {
  const el = $('#server-status');
  el.className = 'status-dot ' + (cls || '');
  el.textContent = text;
}

function renderChips(presets, currentPath) {
  const cur = (currentPath || '').replace(/\/$/, '');
  $('#folder-chips').innerHTML = presets.map(p => `
    <button class="chip ${p.path.replace(/\/$/, '') === cur ? 'active' : ''}" data-path="${escapeAttr(p.path)}">
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M1.5 4.5h4l1.5 1.5h7.5V12a1 1 0 01-1 1h-12a1 1 0 01-1-1V4.5z"/>
      </svg>
      ${escapeHtml(p.label)}
    </button>
  `).join('');
  for (const b of document.querySelectorAll('.chip')) {
    b.addEventListener('click', () => {
      $('#output').value = b.dataset.path;
      markChipActive(b.dataset.path);
    });
  }
}

function markChipActive(path) {
  const norm = (path || '').replace(/\/$/, '');
  for (const b of document.querySelectorAll('.chip')) {
    b.classList.toggle('active', b.dataset.path.replace(/\/$/, '') === norm);
  }
}

async function browseFolder() {
  const btn = $('#browse-btn');
  const initial = $('#output').value.trim();
  btn.disabled = true;
  try {
    const r = await fetch('/api/pick-folder?initial=' + encodeURIComponent(initial));
    const data = await r.json();
    if (data.path) {
      $('#output').value = data.path;
      markChipActive(data.path);
    }
  } catch (e) {
    // silent — user can still type the path
  } finally {
    btn.disabled = false;
  }
}

function setMode(mode) {
  state.mode = mode;
  for (const p of document.querySelectorAll('#format-pills .pill')) {
    p.classList.toggle('active', p.dataset.mode === mode);
  }
  renderQualityOptions();
}

function renderQualityOptions() {
  const sel = $('#quality');
  const lbl = $('#quality-label');
  let opts;
  if (state.mode === 'mp4') {
    lbl.textContent = 'Video quality';
    if (state.inspected?.video_qualities?.length) {
      opts = state.inspected.video_qualities;
    } else {
      opts = [
        { value: 'best', label: 'Best available' },
        { value: '1080', label: '1080p' },
        { value: '720',  label: '720p' },
        { value: '480',  label: '480p' },
        { value: '360',  label: '360p' },
      ];
    }
  } else {
    lbl.textContent = 'Audio bitrate';
    if (state.inspected?.audio_bitrates?.length) {
      opts = state.inspected.audio_bitrates;
    } else {
      opts = [
        { value: 'best', label: 'Best available' },
        { value: '320',  label: '320 kbps' },
        { value: '192',  label: '192 kbps' },
        { value: '128',  label: '128 kbps' },
      ];
    }
  }
  sel.innerHTML = opts
    .map(o => `<option value="${escapeAttr(o.value)}">${escapeHtml(o.label)}</option>`)
    .join('');
}

function renderMeta(info) {
  if (!info) {
    $('#meta-area').innerHTML = '';
    return;
  }
  const dur = info.duration ? formatDuration(info.duration) : '';
  const sub = info.kind === 'playlist'
    ? `Playlist · ${info.count} videos${info.uploader ? ' · ' + escapeHtml(info.uploader) : ''}`
    : [info.uploader, dur].filter(Boolean).map(escapeHtml).join(' · ');
  const thumb = info.thumbnail
    ? `style="background-image: url('${info.thumbnail.replace(/'/g, "%27")}')"`
    : '';
  $('#meta-area').innerHTML = `
    <div class="meta">
      <div class="thumb" ${thumb}></div>
      <div class="meta-text">
        <div class="meta-title">${escapeHtml(info.title)}</div>
        <div class="meta-sub">${sub}</div>
      </div>
    </div>
  `;
}

function formatDuration(sec) {
  sec = Math.floor(sec);
  const h = Math.floor(sec / 3600);
  const m = Math.floor((sec % 3600) / 60);
  const s = sec % 60;
  if (h) return `${h}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;
  return `${m}:${String(s).padStart(2,'0')}`;
}

function formatBytes(n) {
  if (!n && n !== 0) return '–';
  const units = ['B','KB','MB','GB'];
  let i = 0;
  while (n >= 1024 && i < units.length - 1) { n /= 1024; i++; }
  return `${n.toFixed(n >= 10 || i === 0 ? 0 : 1)} ${units[i]}`;
}

function formatTime(sec) {
  if (sec == null || sec < 0) return '–';
  sec = Math.floor(sec);
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return `${m}:${String(s).padStart(2,'0')}`;
}

function escapeHtml(s) {
  return String(s ?? '').replace(/[&<>"']/g, c => ({
    '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
  })[c]);
}
function escapeAttr(s) { return escapeHtml(s); }

async function inspect() {
  const url = $('#url').value.trim();
  if (!url) {
    $('#meta-area').innerHTML = '';
    return;
  }
  if (!state.serverOk) return;
  const btn = $('#fetch-btn');
  btn.disabled = true;
  btn.textContent = 'Fetching…';
  $('#meta-area').innerHTML = '<div class="stage"><span class="spinner"></span>Loading video info…</div>';
  try {
    const r = await fetch('/api/inspect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
    });
    const data = await r.json();
    if (!r.ok) throw new Error(data.error || 'Failed to fetch info');
    state.inspected = data;
    if (data.normalized_url) $('#url').value = data.normalized_url;
    renderMeta(data);
    renderQualityOptions();
  } catch (e) {
    $('#meta-area').innerHTML = `<div class="error">${escapeHtml(e.message)}</div>`;
    state.inspected = null;
    renderQualityOptions();
  } finally {
    btn.disabled = false;
    btn.textContent = 'Fetch info';
  }
}

async function startDownload() {
  const url = $('#url').value.trim();
  if (!url) {
    showError('Paste a YouTube URL first.');
    return;
  }
  const outputDir = $('#output').value.trim() || $('#output').placeholder;
  const params = {
    url,
    mode: state.mode,
    quality: $('#quality').value,
    output_dir: outputDir,
    subtitles: $('#subs').checked,
  };
  setDownloading(true);
  renderProgress({ stage: 'Preparing…' });

  let job;
  try {
    const r = await fetch('/api/download', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    const data = await r.json();
    if (!r.ok) throw new Error(data.error || 'Failed to start');
    job = data.job_id;
  } catch (e) {
    showError(e.message);
    setDownloading(false);
    return;
  }

  const es = new EventSource(`/api/events/${job}`);
  state.job = es;

  let percent = null;
  let stageText = 'Starting…';
  let lastStats = {};

  es.onmessage = (evt) => {
    let msg;
    try { msg = JSON.parse(evt.data); } catch { return; }
    if (msg.event === 'stage') {
      stageText = msg.message;
      renderProgress({ percent, stage: stageText, stats: lastStats });
    } else if (msg.event === 'progress') {
      percent = msg.percent;
      lastStats = msg;
      renderProgress({ percent, stage: stageText, stats: msg });
    } else if (msg.event === 'error') {
      showError(msg.message);
    } else if (msg.event === 'complete') {
      renderComplete(msg);
    } else if (msg.event === 'done') {
      es.close();
      state.job = null;
      setDownloading(false);
    }
  };
  es.onerror = () => {
    es.close();
    state.job = null;
    setDownloading(false);
  };
}

function renderProgress({ percent, stage, stats }) {
  const pct = percent != null ? Math.max(0, Math.min(100, percent)) : null;
  const speed = stats?.speed ? `${formatBytes(stats.speed)}/s` : '–';
  const eta = stats?.eta != null ? formatTime(stats.eta) : '–';
  const sizeNow = stats?.downloaded != null ? formatBytes(stats.downloaded) : '–';
  const sizeTotal = stats?.total != null ? formatBytes(stats.total) : '?';

  $('#progress-area').innerHTML = `
    <div class="progress-wrap">
      <div class="bar">
        <div class="bar-fill ${pct == null ? 'indeterminate' : ''}" style="width:${pct != null ? pct.toFixed(1) : 0}%"></div>
      </div>
      <div class="progress-stats">
        <div><span class="stat-label">Progress</span><span class="stat-val">${pct != null ? pct.toFixed(1) + '%' : '—'}</span></div>
        <div><span class="stat-label">Size</span><span class="stat-val">${sizeNow} / ${sizeTotal}</span></div>
        <div><span class="stat-label">Speed</span><span class="stat-val">${speed}</span></div>
        <div><span class="stat-label">ETA</span><span class="stat-val">${eta}</span></div>
      </div>
      <div class="stage"><span class="spinner"></span>${escapeHtml(stage || '')}</div>
    </div>
  `;
}

function renderComplete(msg) {
  const files = msg.files || [];
  const items = files.length
    ? files.map(f => `
        <li>
          <span class="fname" title="${escapeAttr(f)}">${escapeHtml(basename(f))}</span>
          <button class="link-btn" data-path="${escapeAttr(f)}">Show in Finder</button>
        </li>
      `).join('')
    : `<li><span class="fname">Saved to ${escapeHtml(msg.output_dir)}</span>
         <button class="link-btn" data-path="${escapeAttr(msg.output_dir)}">Open folder</button></li>`;

  $('#progress-area').innerHTML = `
    <div class="success">
      <h3>
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M3 8l3 3 7-7"/>
        </svg>
        Download complete
      </h3>
      <ul class="file-list">${items}</ul>
    </div>
  `;
  for (const b of document.querySelectorAll('.link-btn')) {
    b.addEventListener('click', () => {
      fetch('/api/reveal?path=' + encodeURIComponent(b.dataset.path));
    });
  }
}

function basename(p) {
  const m = p.match(/[^/\\]+$/);
  return m ? m[0] : p;
}

function showError(msg) {
  const area = $('#progress-area');
  area.innerHTML = `<div class="error">${escapeHtml(msg)}</div>`;
}

function setDownloading(on) {
  $('#download-btn').disabled = on;
  $('#download-btn').innerHTML = on
    ? '<span class="spinner" style="border-color:rgba(255,255,255,0.4);border-top-color:white;"></span>Downloading…'
    : '<svg class="icon" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 2v9m0 0l-3.5-3.5M8 11l3.5-3.5M2.5 13.5h11"/></svg>Download';
  $('#fetch-btn').disabled = on;
  $('#browse-btn').disabled = on;
}

// ---- init ----
for (const p of document.querySelectorAll('#format-pills .pill')) {
  p.addEventListener('click', () => setMode(p.dataset.mode));
}
$('#fetch-btn').addEventListener('click', inspect);
$('#download-btn').addEventListener('click', startDownload);
$('#browse-btn').addEventListener('click', browseFolder);
$('#url').addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    e.preventDefault();
    inspect();
  }
});
$('#url').addEventListener('paste', () => {
  setTimeout(() => {
    if ($('#url').value.trim()) inspect();
  }, 50);
});
$('#output').addEventListener('input', () => {
  markChipActive($('#output').value.trim());
});

loadDefaults();
renderQualityOptions();
</script>
</body>
</html>
"""
