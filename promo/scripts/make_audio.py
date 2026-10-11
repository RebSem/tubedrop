#!/usr/bin/env python3
"""
Synthesises every sound in the promo from scratch (numpy only), so there is
nothing to license: UI clicks, whooshes, impacts, glitches, typing, and a
temporary 120-BPM guide track laid out on the same beat grid as the edit.

    python3 scripts/make_audio.py

Reads BPM and TOTAL_BEATS from src/config.ts so beat-length sounds (riser,
ticks, progress) always match the edit.
"""
import os
import re
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SFX = os.path.join(ROOT, "public", "sfx")
MUSIC = os.path.join(ROOT, "public", "music")
os.makedirs(SFX, exist_ok=True)
os.makedirs(MUSIC, exist_ok=True)

cfg = open(os.path.join(ROOT, "src", "config.ts")).read()
BPM = float(re.search(r"export const BPM = ([\d.]+)", cfg).group(1))
TOTAL_BEATS = int(re.search(r"export const TOTAL_BEATS = (\d+)", cfg).group(1))
SPB = 60.0 / BPM
SR = 48000
rng = np.random.default_rng(7)


# ───────────────────────── helpers ─────────────────────────

def tt(sec):
    return np.arange(int(sec * SR)) / SR


def noise(n):
    return rng.standard_normal(n)


def band(x, lo, hi, soft=0.15):
    """FFT band-pass with smooth (log-domain) edges."""
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    lf = np.log(np.maximum(f, 1.0))
    g = 1 / (1 + np.exp(-(lf - np.log(lo)) / soft)) * 1 / (1 + np.exp((lf - np.log(hi)) / soft))
    return np.fft.irfft(X * g, n)


def sweep_noise(sec, fc_curve, width=0.55, bands=14, lo=120, hi=12000):
    """Noise whose spectral centre follows fc_curve(t∈0..1) — a cheap time-varying filter."""
    n = int(sec * SR)
    k = np.linspace(0, 1, n)
    fc = np.log(fc_curve(k))
    centres = np.geomspace(lo, hi, bands)
    out = np.zeros(n)
    for i, c in enumerate(centres):
        a = c / 1.35
        b = c * 1.35
        sig = band(noise(n), a, b, 0.08)
        g = np.exp(-((np.log(c) - fc) ** 2) / (2 * width**2))
        out += sig * g
    return out / (np.max(np.abs(out)) + 1e-9)


def sine_glide(sec, f0, f1, curve=1.0):
    n = int(sec * SR)
    k = np.linspace(0, 1, n) ** curve
    f = f0 * (f1 / f0) ** k
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph)


def env_exp(n, decay):
    return np.exp(-np.arange(n) / SR / decay)


def env_ar(n, a, r):
    t_ = np.arange(n) / SR
    e = np.minimum(1, t_ / max(a, 1e-4)) * np.exp(-np.maximum(0, t_ - a) / r)
    return e


def reverb(x, sec=0.9, mix=0.25, decay=0.35):
    ir = noise(int(sec * SR)) * env_exp(int(sec * SR), decay)
    ir = band(ir, 200, 9000)
    ir /= np.sqrt(np.sum(ir**2)) + 1e-9
    n = len(x) + len(ir)
    y = np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(ir, n), n)[: len(x) + len(ir) - 1]
    dry = np.concatenate([x, np.zeros(len(y) - len(x))])
    return dry * (1 - mix) + y * mix * 0.6


def norm(x, peak=0.9):
    m = np.max(np.abs(x)) + 1e-9
    return x / m * peak


def stereo(x, width=0.0, pan=0.0):
    if x.ndim == 2:
        return x
    l = x * (1 - max(0, pan))
    r = x * (1 + min(0, pan))
    if width > 0:
        d = int(width * 0.012 * SR)
        r = np.concatenate([np.zeros(d), r])[: len(x)]
    return np.stack([l, r], 1)


def write(path, x):
    if x.ndim == 1:
        x = stereo(x)
    x = np.clip(x, -1, 1)
    data = (x * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


def sfx(name, x, peak=0.9):
    write(os.path.join(SFX, name + ".wav"), norm(x, peak))


def place(dst, src, at_sec, gain=1.0):
    i = int(at_sec * SR)
    if i >= len(dst):
        return
    if src.ndim == 1 and dst.ndim == 2:
        src = stereo(src)
    j = min(len(dst), i + len(src))
    dst[i:j] += src[: j - i] * gain


# ───────────────────────── drum voices ─────────────────────────

def kick(sec=0.45, punch=1.0):
    n = int(sec * SR)
    t_ = np.arange(n) / SR
    f = 46 + 120 * np.exp(-t_ * 32)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t_ * 7.5)
    click = band(noise(n), 1500, 7000) * np.exp(-t_ * 320) * 0.5 * punch
    return np.tanh((body + click) * 1.6)


def clap(sec=0.35):
    n = int(sec * SR)
    t_ = np.arange(n) / SR
    nz = band(noise(n), 900, 7000)
    e = np.zeros(n)
    for o in (0, 0.011, 0.022):
        e += np.where(t_ >= o, np.exp(-(t_ - o) * 90), 0)
    e += np.exp(-t_ * 16) * 0.5
    return nz * e


def hat(sec=0.05, open_=False):
    n = int((0.22 if open_ else sec) * SR)
    t_ = np.arange(n) / SR
    return band(noise(n), 7000, 16000) * np.exp(-t_ * (14 if open_ else 95))


def snare(sec=0.2):
    n = int(sec * SR)
    t_ = np.arange(n) / SR
    tone = np.sin(2 * np.pi * 190 * t_) * np.exp(-t_ * 30)
    nz = band(noise(n), 1500, 9000) * np.exp(-t_ * 22)
    return tone * 0.6 + nz


# ───────────────────────── SFX ─────────────────────────

def make_sfx():
    # deep cinematic impact
    n = int(1.6 * SR)
    t_ = np.arange(n) / SR
    sub = np.sin(2 * np.pi * np.cumsum(32 + 70 * np.exp(-t_ * 9)) / SR) * np.exp(-t_ * 2.2)
    crack = band(noise(n), 200, 5000) * np.exp(-t_ * 26)
    sfx("boom", reverb(np.tanh(sub * 1.8 + crack * 0.6), 1.4, 0.3, 0.6))

    # punchy hit (text slams)
    h = kick(0.5) * 0.9
    h[: len(clap(0.3))] += clap(0.3) * 0.5
    sfx("hit", reverb(h, 0.7, 0.18, 0.25), 0.85)

    # split-flap flutter
    out = np.zeros(int(1.1 * SR))
    pos = 0.0
    while pos < 0.95:
        c = int(0.006 * SR)
        click = band(noise(c), 1800, 7000) * env_exp(c, 0.0015)
        knock = np.sin(2 * np.pi * (260 + rng.random() * 120) * tt(0.012)) * env_exp(int(0.012 * SR), 0.003)
        place(out, click, pos, 0.6 + rng.random() * 0.4)
        place(out, knock, pos, 0.4)
        pos += 0.018 + rng.random() * 0.02 + max(0, pos - 0.6) * 0.08
    sfx("flaps", out, 0.8)

    # blips
    for name, f0, f1, d in [
        ("blip", 1320, 1320, 0.07),
        ("blip_down1", 980, 620, 0.12),
        ("blip_down2", 760, 460, 0.12),
        ("blip_down3", 560, 300, 0.14),
    ]:
        x = sine_glide(d, f0, f1) * env_exp(int(d * SR), d / 3)
        sfx(name, x, 0.7)

    # error "bonks"
    for name, f in [("error", 440), ("error1", 587), ("error2", 659), ("error3", 740)]:
        d = 0.16
        t2 = tt(d)
        sq = sum(np.sin(2 * np.pi * f * k * t2) / k for k in (1, 3, 5, 7))
        x = sq * env_exp(len(t2), 0.05)
        x2 = np.concatenate([x, np.zeros(int(0.03 * SR)), x * 0.7])
        sfx(name, x2, 0.6)

    # toggle
    d = 0.12
    x = np.zeros(int(d * SR))
    place(x, band(noise(int(0.004 * SR)), 2000, 9000), 0)
    place(x, np.sin(2 * np.pi * 1700 * tt(0.02)) * env_exp(int(0.02 * SR), 0.005) * 0.5, 0.0)
    place(x, np.sin(2 * np.pi * 150 * tt(0.08)) * env_exp(int(0.08 * SR), 0.02), 0.005)
    sfx("toggle", x, 0.8)

    # pop
    sfx("pop", sine_glide(0.08, 950, 260, 0.5) * env_exp(int(0.08 * SR), 0.03), 0.7)

    # mouse click
    x = np.zeros(int(0.05 * SR))
    for o, g in ((0, 1), (0.018, 0.6)):
        c = int(0.004 * SR)
        place(x, band(noise(c), 2500, 9000) * env_exp(c, 0.0008), o, g)
    sfx("click", x, 0.75)

    # key press
    x = np.zeros(int(0.08 * SR))
    c = int(0.03 * SR)
    place(x, band(noise(c), 600, 3500) * env_exp(c, 0.006), 0)
    place(x, band(noise(int(0.004 * SR)), 3000, 9000), 0.0)
    sfx("keypress", x, 0.8)

    # tick + tick run
    c = int(0.012 * SR)
    tick = band(noise(c), 5000, 12000) * env_exp(c, 0.002) + np.sin(2 * np.pi * 3200 * tt(0.012)) * env_exp(c, 0.003) * 0.4
    sfx("tick", tick, 0.6)
    run = np.zeros(int(2 * SPB * SR) + c)
    for i in range(8):
        place(run, tick, i * SPB / 4, 0.7 + (i % 4 == 0) * 0.3)
    sfx("ticks", run, 0.6)

    # whooshes
    sfx("whoosh", sweep_noise(0.5, lambda k: 300 * (4000 / 300) ** np.sin(np.pi * k * 0.9)) * np.sin(np.pi * np.linspace(0, 1, int(0.5 * SR))) ** 2, 0.8)
    sfx("whoosh_long", sweep_noise(1.0, lambda k: 200 * (6000 / 200) ** np.sin(np.pi * k * 0.85)) * np.sin(np.pi * np.linspace(0, 1, int(1.0 * SR))) ** 1.5, 0.8)
    n = int(0.55 * SR)
    up = sweep_noise(0.55, lambda k: 250 * (9000 / 250) ** k) * np.linspace(0, 1, n) ** 2
    up += sine_glide(0.55, 300, 2400, 1.5) * np.linspace(0, 1, n) ** 3 * 0.25
    sfx("whoosh_up", up, 0.8)
    n = int(0.28 * SR)
    sfx("swipe", sweep_noise(0.28, lambda k: 800 * (7000 / 800) ** k) * np.sin(np.pi * np.linspace(0, 1, n)), 0.7)

    # plane fly-by (doppler)
    d = 1.3
    n = int(d * SR)
    k = np.linspace(0, 1, n)
    f = 210 * (1.25 - 0.5 / (1 + np.exp(-(k - 0.5) * 10)))
    tone = sum(np.sin(2 * np.pi * np.cumsum(f * m) / SR) / m for m in (1, 2, 3, 5))
    amp = np.exp(-((k - 0.5) ** 2) / 0.05)
    air = sweep_noise(d, lambda k: 400 * (5000 / 400) ** np.exp(-((k - 0.5) ** 2) / 0.04))
    x = (tone * 0.35 + air) * amp
    l = x * (1 - k) + x * 0.3
    r = x * k + x * 0.3
    write(os.path.join(SFX, "swish.wav"), norm(np.stack([l, r], 1), 0.8))

    # stamp thud
    n = int(0.4 * SR)
    t_ = np.arange(n) / SR
    thud = np.sin(2 * np.pi * np.cumsum(70 + 90 * np.exp(-t_ * 40)) / SR) * np.exp(-t_ * 12)
    slap = band(noise(n), 300, 3000) * np.exp(-t_ * 45)
    sfx("stamp", reverb(np.tanh((thud + slap * 0.8) * 2), 0.5, 0.15, 0.15), 0.95)

    # everything falls
    d = 0.9
    sfx("fall", sine_glide(d, 1400, 160, 0.8) * np.linspace(1, 0.2, int(d * SR)) * 0.4 + sweep_noise(d, lambda k: 3000 * (200 / 3000) ** k) * 0.6, 0.7)

    # glitch stutter
    d = 0.7
    out = np.zeros(int(d * SR))
    pos = 0.0
    while pos < d - 0.03:
        seg = 0.015 + rng.random() * 0.05
        nn = int(seg * SR)
        kind = rng.integers(0, 3)
        if kind == 0:
            s = np.sign(np.sin(2 * np.pi * rng.uniform(80, 1200) * tt(seg)))
        elif kind == 1:
            s = np.round(noise(nn) * 3) / 3
        else:
            s = np.repeat(noise(nn // 8 + 1), 8)[:nn]
        place(out, s * rng.uniform(0.3, 1), pos)
        pos += seg + (rng.random() < 0.3) * 0.02
    sfx("glitch", out, 0.7)

    # typing
    def typing(sec, rate=15):
        out = np.zeros(int(sec * SR) + int(0.05 * SR))
        p = 0.0
        while p < sec:
            c = int(0.022 * SR)
            k_ = band(noise(c), 900 + rng.random() * 900, 5000) * env_exp(c, 0.004)
            place(out, k_, p, 0.5 + rng.random() * 0.5)
            p += 1 / rate * (0.6 + rng.random() * 0.8)
        return out

    sfx("type_long", typing(1.6), 0.7)
    sfx("type_short", typing(0.6), 0.7)

    # CRT power-off
    d = 0.45
    n = int(d * SR)
    z = sine_glide(d, 3600, 50, 0.6) * np.exp(-np.linspace(0, 4, n))
    crackle = band(noise(n), 1000, 8000) * (rng.random(n) < 0.03) * 2
    thump = np.zeros(n)
    place(thump, np.sin(2 * np.pi * 60 * tt(0.15)) * env_exp(int(0.15 * SR), 0.05), 0.0)
    sfx("zap", z * 0.6 + crackle * 0.3 + thump, 0.8)

    # riser (exactly 4 beats, ends on the drop)
    d = 4 * SPB
    n = int(d * SR)
    k = np.linspace(0, 1, n)
    r = sweep_noise(d, lambda k: 200 * (11000 / 200) ** (k**1.4), width=0.5) * k**2.2
    r += sine_glide(d, 110, 1760, 1.6) * k**2.5 * 0.35
    r += sine_glide(d, 165, 2640, 1.6) * k**2.5 * 0.2
    r[-int(0.01 * SR):] *= np.linspace(1, 0, int(0.01 * SR))
    sfx("riser", r, 0.8)

    # bell ding
    d = 1.4
    t2 = tt(d)
    bell = sum(a * np.sin(2 * np.pi * 1318.5 * m * t2) * np.exp(-t2 * dd) for m, a, dd in ((1, 1, 3), (2.0, 0.5, 5), (2.76, 0.35, 7), (5.4, 0.2, 11)))
    bell += sum(a * np.sin(2 * np.pi * 1975.5 * m * t2) * np.exp(-np.maximum(0, t2 - 0.09) * dd) * (t2 > 0.09) for m, a, dd in ((1, 0.8, 3), (2.0, 0.3, 6)))
    sfx("ding", reverb(bell, 1.0, 0.3, 0.4), 0.6)

    # sparkle
    d = 1.0
    out = np.zeros(int(d * SR))
    for i in range(26):
        f = rng.uniform(2200, 7000)
        s = np.sin(2 * np.pi * f * tt(0.12)) * env_exp(int(0.12 * SR), 0.025)
        place(out, s, rng.uniform(0, 0.7), rng.uniform(0.2, 0.7))
    sfx("sparkle", reverb(out, 0.8, 0.35, 0.3), 0.55)

    # progress — arpeggio accelerating up over 1.4 beats
    d = 1.4 * SPB + 0.1
    out = np.zeros(int(d * SR))
    notes = [60, 63, 67, 70, 72, 75, 79, 82, 84, 87, 91, 94, 96]
    for i, m in enumerate(notes):
        pos = (i / len(notes)) ** 0.75 * 1.4 * SPB
        f = 440 * 2 ** ((m - 69) / 12)
        s = np.sin(2 * np.pi * f * tt(0.07)) * env_exp(int(0.07 * SR), 0.02)
        place(out, s, pos, 0.6)
    sfx("progress", out, 0.6)

    # soft thump for the end-card logo landing
    n = int(0.5 * SR)
    t_ = np.arange(n) / SR
    th = np.sin(2 * np.pi * np.cumsum(90 + 70 * np.exp(-t_ * 30)) / SR) * np.exp(-t_ * 9)
    boing = np.sin(2 * np.pi * np.cumsum(240 + 40 * np.sin(t_ * 60) * np.exp(-t_ * 8)) / SR) * np.exp(-t_ * 10) * 0.25
    sfx("thump", reverb(th + boing, 0.6, 0.2, 0.25), 0.8)


# ───────────────────────── temp guide track ─────────────────────────

def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def saw(f, sec, harmonics=18, bright=1.0, detune=0.0):
    t_ = tt(sec)
    out = np.zeros(len(t_))
    for k in range(1, harmonics + 1):
        if f * k > 16000:
            break
        w = 1 / k * (1 / (1 + (k / (6 * bright + 0.5)) ** 2))
        out += w * np.sin(2 * np.pi * f * (1 + detune) * k * t_ + k * 0.37)
    return out


def make_track():
    total = TOTAL_BEATS * SPB + 2.5
    L = int(total * SR)
    mix = np.zeros((L, 2))
    drums = np.zeros((L, 2))

    prog = [  # one chord per bar (4 beats): Fm, Db, Ab, Eb
        (41, [53, 56, 60]),
        (37, [49, 53, 56]),
        (44, [56, 60, 63]),
        (39, [51, 55, 58]),
    ]

    K = kick()
    CL = clap()
    HH = hat()
    OH = hat(open_=True)
    SN = snare(0.12)

    def section(b):
        if b < 8:
            return "hook"
        if b < 16:
            return "scam"
        if b < 22:
            return "cli"
        if b < 28:
            return "build"
        if b < 44:
            return "drop"
        if b < 52:
            return "feat"
        return "outro"

    for b16 in range(TOTAL_BEATS * 4):
        b = b16 / 4
        s = section(b)
        at = b * SPB
        on_beat = b16 % 4 == 0
        beat_in_bar = int(b) % 4

        # kick
        if s in ("hook", "scam", "drop", "feat") and on_beat:
            place(drums, K, at, 0.95)
        if s == "cli" and on_beat and beat_in_bar in (0,):
            place(drums, K, at, 0.6)
        if s == "build" and on_beat and b < 27:
            place(drums, K, at, 0.85)
        if s == "outro" and on_beat and b in (52, 53, 54):
            place(drums, K, at, 1.0)

        # clap on 2 & 4
        if s in ("hook", "scam", "drop", "feat") and on_beat and beat_in_bar in (1, 3):
            place(drums, CL, at, 0.55)

        # hats
        if s in ("hook", "drop", "feat") and b16 % 2 == 1:
            place(drums, stereo(HH, pan=0.3), at, 0.28)
        if s in ("scam",) and True:
            place(drums, stereo(HH, pan=-0.3), at, 0.22 if b16 % 2 else 0.12)
        if s == "cli" and b16 % 2 == 1:
            place(drums, HH, at, 0.12)
        if s == "feat" and b16 % 4 == 2:
            place(drums, OH, at, 0.18)

        # build snare roll
        if s == "build" and b >= 24 and b < 27.75:
            step = 2 if b < 26 else (1 if b < 27 else 0.5)
            if (b16 % step if step >= 1 else 0) == 0:
                g = 0.18 + (b - 24) / 4 * 0.45
                place(drums, SN, at, g)
                if step == 0.5:
                    place(drums, SN, at + SPB / 8, g)

    # bass + chords + arp
    for bar in range(TOTAL_BEATS // 4):
        b0 = bar * 4
        s = section(b0)
        root, chord = prog[bar % 4]
        bar_t = b0 * SPB
        bright = {"hook": 0.9, "scam": 1.0, "cli": 0.25, "build": 0.6, "drop": 1.4, "feat": 1.3, "outro": 0.9}[s]

        # pad
        if s != "outro" or b0 < 56:
            dur = 4 * SPB
            pad = np.zeros(int(dur * SR))
            for m in chord:
                pad += saw(midi(m), dur, 10, bright, 0.003) + saw(midi(m), dur, 10, bright, -0.004)
            pad *= env_ar(len(pad), 0.04 if s in ("drop", "feat") else 0.3, 3.0)
            g = {"hook": 0.07, "scam": 0.06, "cli": 0.05, "build": 0.06, "drop": 0.085, "feat": 0.085, "outro": 0.08}[s]
            place(mix, stereo(pad, width=1.0), bar_t, g)

        # bass on 8ths (pumping)
        if s in ("hook", "scam", "drop", "feat", "build"):
            for e in range(8):
                if s == "build" and b0 + e / 2 >= 27:
                    continue
                f = midi(root + (12 if (s in ("scam", "feat") and e % 2) else 0))
                n_ = saw(f, SPB / 2 * 0.9, 12, 0.8 * bright)
                n_ *= env_ar(len(n_), 0.005, 0.12)
                place(mix, n_, bar_t + e * SPB / 2, 0.22)

        # arp in drop/feat
        if s in ("drop", "feat"):
            tones = chord + [c + 12 for c in chord]
            for i in range(16):
                m = tones[(i * 2 + (i // 4)) % len(tones)] + 12
                n_ = saw(midi(m), SPB / 4 * 0.9, 6, 1.5)
                n_ *= env_ar(len(n_), 0.002, 0.06)
                place(mix, stereo(n_, pan=0.25 if i % 2 else -0.25), bar_t + i * SPB / 4, 0.06)

    # stabs on Install / Paste / Fly
    for b in (52, 53, 54):
        root, chord = prog[0]
        st = np.zeros(int(1.2 * SR))
        for m in chord + [c + 12 for c in chord]:
            st += saw(midi(m), 1.2, 14, 1.6)
        st *= env_ar(len(st), 0.003, 0.25)
        place(mix, stereo(st, width=1.0), b * SPB, 0.12)

    # final resolving chord (Db maj7-ish) ringing out
    fin = np.zeros(int(6 * SR))
    for m in (49, 53, 56, 60, 65):
        fin += saw(midi(m), 6, 10, 0.7, 0.002) + saw(midi(m), 6, 10, 0.7, -0.003)
    fin *= env_ar(len(fin), 0.3, 2.5)
    place(mix, stereo(fin, width=1.0), 55 * SPB, 0.07)

    # sidechain-style pump on the music bus
    pump = np.ones(L)
    for b in range(TOTAL_BEATS):
        if section(b) in ("hook", "scam", "drop", "feat"):
            i = int(b * SPB * SR)
            n_ = int(SPB * SR)
            j = min(L, i + n_)
            pump[i:j] = 1 - 0.55 * np.exp(-np.arange(j - i) / SR / 0.09)
    mix *= pump[:, None]

    # silence gap just before the drop
    i0 = int(27.75 * SPB * SR)
    i1 = int(28 * SPB * SR)
    mix[i0:i1] *= 0.05
    drums[i0:i1] *= 0.0

    out = mix + drums * 0.9
    out = np.tanh(out * 1.4) / np.tanh(1.4)
    out = out / (np.max(np.abs(out)) + 1e-9) * 0.89
    write(os.path.join(MUSIC, "temp-beat.wav"), out)


if __name__ == "__main__":
    make_sfx()
    make_track()
    print(f"sfx + temp beat written · BPM={BPM:g} · {TOTAL_BEATS} beats")
