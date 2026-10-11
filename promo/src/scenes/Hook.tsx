import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {C, FPB} from '../config';
import {display, displayMono, mono, sans, serif} from '../fonts';
import {BACK_OUT, EXPO_IN, EXPO_OUT, pulse, rand, sp, tw, useBeat} from '../anim';
import {DirBlur, I, Sfx} from '../components/common';

/* ═════════════ split-flap tile ═════════════ */

const GLYPHS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
const FLIP_FRAMES = 1.6;

const Half: React.FC<{
  ch: string;
  part: 'top' | 'bottom';
  w: number;
  h: number;
  fs: number;
  color: string;
  style?: React.CSSProperties;
}> = ({ch, part, w, h, fs, color, style}) => (
  <div
    style={{
      position: 'absolute',
      left: 0,
      top: part === 'top' ? 0 : h / 2,
      width: w,
      height: h / 2,
      overflow: 'hidden',
      background: part === 'top' ? 'linear-gradient(180deg,#26262E,#1D1D24)' : 'linear-gradient(180deg,#1A1A20,#141419)',
      borderRadius: part === 'top' ? '12px 12px 0 0' : '0 0 12px 12px',
      backfaceVisibility: 'hidden',
      ...style,
    }}
  >
    <div
      style={{
        position: 'absolute',
        left: 0,
        top: part === 'top' ? 0 : -h / 2,
        width: w,
        height: h,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontFamily: displayMono,
        fontWeight: 800,
        fontSize: fs,
        lineHeight: 1,
        color,
      }}
    >
      {ch}
    </div>
  </div>
);

const FlapTile: React.FC<{
  target: string;
  flips: number;
  seed: number;
  start: number; // frame
  w: number;
  h: number;
  fs: number;
  color?: string;
}> = ({target, flips, seed, start, w, h, fs, color = '#F4F4F6'}) => {
  const frame = useCurrentFrame();
  const local = frame - start;
  const charAt = (k: number) => {
    if (k <= 0) return ' ';
    if (k >= flips) return target;
    return GLYPHS[Math.floor(rand(seed * 17.3 + k * 3.1) * GLYPHS.length)];
  };
  const n = Math.floor(local / FLIP_FRAMES);
  const settled = local < 0 || n >= flips;
  const cur = local < 0 ? ' ' : charAt(Math.min(n, flips));
  const next = charAt(n + 1);
  const p = settled ? 0 : (local % FLIP_FRAMES) / FLIP_FRAMES;

  return (
    <div style={{position: 'relative', width: w, height: h, perspective: 700}}>
      {settled ? (
        <>
          <Half ch={cur} part="top" w={w} h={h} fs={fs} color={color} />
          <Half ch={cur} part="bottom" w={w} h={h} fs={fs} color={color} />
        </>
      ) : (
        <>
          <Half ch={next} part="top" w={w} h={h} fs={fs} color={color} />
          <Half ch={p < 0.5 ? cur : next} part="bottom" w={w} h={h} fs={fs} color={color} />
          {p < 0.5 ? (
            <Half
              ch={cur}
              part="top"
              w={w}
              h={h}
              fs={fs}
              color={color}
              style={{
                transformOrigin: '50% 100%',
                transform: `rotateX(${-p * 180}deg)`,
                filter: `brightness(${1 - p * 1.1})`,
              }}
            />
          ) : (
            <Half
              ch={next}
              part="bottom"
              w={w}
              h={h}
              fs={fs}
              color={color}
              style={{
                transformOrigin: '50% 0%',
                transform: `rotateX(${(1 - p) * 180}deg)`,
                filter: `brightness(${0.45 + (p - 0.5) * 1.1})`,
              }}
            />
          )}
        </>
      )}
      {/* hinge */}
      <div style={{position: 'absolute', left: 0, right: 0, top: h / 2 - 1.5, height: 3, background: '#060608'}} />
      <div style={{position: 'absolute', left: -3, top: h / 2 - 7, width: 6, height: 14, borderRadius: 2, background: '#33333B'}} />
      <div style={{position: 'absolute', right: -3, top: h / 2 - 7, width: 6, height: 14, borderRadius: 2, background: '#33333B'}} />
    </div>
  );
};

const Board: React.FC<{t: number}> = ({t}) => {
  const rows = ['BOARDING', 'IN 2 HRS'];
  const tw_ = 112;
  const th = 158;
  const gap = 10;
  const blink = Math.floor(t * 4) % 2 === 0;
  return (
    <div style={{display: 'flex', flexDirection: 'column', gap: 26}}>
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontFamily: mono, fontWeight: 700, fontSize: 30, letterSpacing: '0.16em', color: C.amber}}>
        <div style={{display: 'flex', alignItems: 'center', gap: 16}}>
          <I.plane size={36} color={C.amber} />
          DEPARTURES
        </div>
        <div style={{color: '#8A8A92', letterSpacing: '0.12em'}}>GATE 12 · 14:05</div>
      </div>
      {rows.map((row, r) => (
        <div key={r} style={{display: 'flex', gap}}>
          {row.split('').map((ch, i) => (
            <FlapTile
              key={i}
              target={ch}
              flips={ch === ' ' ? 2 : 5 + Math.round(i * 0.55) + r * 2}
              seed={r * 10 + i + 1}
              start={Math.round(i * 0.5 + r * 2) - 4}
              w={tw_}
              h={th}
              fs={124}
            />
          ))}
        </div>
      ))}
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontFamily: mono, fontWeight: 600, fontSize: 26, letterSpacing: '0.12em', color: '#8A8A92'}}>
        <div>FLIGHT TD 001 → OFFLINE</div>
        <div style={{display: 'flex', alignItems: 'center', gap: 12, color: t > 1.5 ? C.amber : '#444', opacity: t > 1.5 && blink ? 1 : 0.35}}>
          <div style={{width: 16, height: 16, borderRadius: 8, background: 'currentColor', boxShadow: '0 0 18px currentColor'}} />
          FINAL CALL SOON
        </div>
      </div>
    </div>
  );
};

/* ═════════════ thumbnail of "the interview" ═════════════ */

const InterviewThumb: React.FC<{w: number; h: number}> = ({w, h}) => (
  <svg width={w} height={h} viewBox="0 0 968 545" style={{display: 'block'}}>
    <defs>
      <linearGradient id="studio" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stopColor="#3B2416" />
        <stop offset="0.55" stopColor="#1E1410" />
        <stop offset="1" stopColor="#0E0A09" />
      </linearGradient>
      <radialGradient id="lampL" cx="0.22" cy="0.25" r="0.5">
        <stop offset="0" stopColor="#FF9A4A" stopOpacity="0.55" />
        <stop offset="1" stopColor="#FF9A4A" stopOpacity="0" />
      </radialGradient>
      <radialGradient id="lampR" cx="0.8" cy="0.2" r="0.45">
        <stop offset="0" stopColor="#4A7BFF" stopOpacity="0.45" />
        <stop offset="1" stopColor="#4A7BFF" stopOpacity="0" />
      </radialGradient>
    </defs>
    <rect width="968" height="545" fill="url(#studio)" />
    <rect width="968" height="545" fill="url(#lampL)" />
    <rect width="968" height="545" fill="url(#lampR)" />
    {/* shelves / bokeh */}
    {[...Array(14)].map((_, i) => (
      <circle key={i} cx={60 + rand(i) * 850} cy={40 + rand(i + 50) * 200} r={8 + rand(i + 9) * 22} fill={i % 3 ? '#FFB36B' : '#7FA6FF'} opacity={0.08 + rand(i + 3) * 0.12} />
    ))}
    {/* left guest */}
    <path d="M150 545 C150 420 210 360 300 360 C390 360 450 420 450 545 Z" fill="#0B0807" />
    <circle cx="300" cy="275" r="78" fill="#0B0807" />
    <path d="M232 250 C240 200 290 185 330 200" stroke="#FF9A4A" strokeOpacity="0.5" strokeWidth="5" fill="none" strokeLinecap="round" />
    {/* right host */}
    <path d="M520 545 C520 430 580 372 668 372 C756 372 816 430 816 545 Z" fill="#0B0807" />
    <circle cx="668" cy="288" r="74" fill="#0B0807" />
    <path d="M735 262 C728 214 690 200 652 210" stroke="#7FA6FF" strokeOpacity="0.55" strokeWidth="5" fill="none" strokeLinecap="round" />
    {/* mics */}
    <rect x="388" y="330" width="44" height="92" rx="22" fill="#2A2A30" />
    <path d="M410 422 L410 470 L470 500" stroke="#2A2A30" strokeWidth="10" fill="none" />
    <rect x="540" y="340" width="44" height="92" rx="22" fill="#2A2A30" />
    <path d="M562 432 L562 480 L500 505" stroke="#2A2A30" strokeWidth="10" fill="none" />
    {/* table */}
    <rect x="0" y="500" width="968" height="45" fill="#140E0B" />
  </svg>
);

/* ═════════════ wifi icon ═════════════ */

const C0 = 5; // part C start (beats)
const B0 = 3; // part B start (beats)

const Wifi: React.FC<{t: number; size: number}> = ({t, size}) => {
  // arcs disappear on 16ths, then the dot dies on the next 8th
  const arc = (d: string, at: number, key: string) => {
    const gone = t >= at;
    const k = sp(t, at, {damping: 12, stiffness: 260});
    return (
      <path
        key={key}
        d={d}
        stroke={gone ? '#3A3A44' : '#FFFFFF'}
        strokeWidth={2.2}
        fill="none"
        strokeLinecap="round"
        style={{
          transformOrigin: '12px 20px',
          transform: gone ? `scale(${1 + (1 - k) * 0.15})` : undefined,
          opacity: gone ? 0.35 : 1,
        }}
      />
    );
  };
  const dead = t >= C0 + 0.5;
  const slash = tw(t, C0 + 0.5, C0 + 0.75, 0, 1, EXPO_OUT);
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" style={{overflow: 'visible'}}>
      {arc('M2 8.82a15 15 0 0 1 20 0', C0 + 0.125, 'a1')}
      {arc('M5 12.86a10 10 0 0 1 14 0', C0 + 0.25, 'a2')}
      {arc('M8.5 16.43a5 5 0 0 1 7 0', C0 + 0.375, 'a3')}
      <circle cx="12" cy="20" r="1.5" fill={dead ? C.red : '#FFFFFF'} />
      <line
        x1="3"
        y1="3"
        x2={3 + 18 * slash}
        y2={3 + 18 * slash}
        stroke={C.red}
        strokeWidth={2.4}
        strokeLinecap="round"
        opacity={slash > 0 ? 1 : 0}
      />
    </svg>
  );
};

/* ═════════════ the airplane-mode toggle ═════════════ */

const PlaneToggle: React.FC<{on: number; scale?: number}> = ({on, scale = 1}) => {
  const W_ = 440 * scale;
  const H_ = 250 * scale;
  const knob = H_ - 28 * scale;
  return (
    <div
      style={{
        width: W_,
        height: H_,
        borderRadius: H_ / 2,
        background: on > 0.5 ? '#E07F00' : '#3A3A44',
        position: 'relative',
        boxShadow: 'inset 0 6px 16px rgba(0,0,0,0.3), 0 0 0 10px rgba(11,11,16,0.10), 0 24px 50px -16px rgba(11,11,16,0.45)',
      }}
    >
      <div
        style={{
          position: 'absolute',
          top: 14 * scale,
          left: 14 * scale + on * (W_ - knob - 28 * scale),
          width: knob,
          height: knob,
          borderRadius: '50%',
          background: '#fff',
          boxShadow: '0 10px 30px rgba(0,0,0,0.3)',
          display: 'grid',
          placeItems: 'center',
        }}
      >
        <I.plane size={knob * 0.52} color={on > 0.5 ? C.orange : '#8A8A92'} />
      </div>
    </div>
  );
};

/* ═════════════ the scene ═════════════ */

export const Hook: React.FC = () => {
  const t = useBeat();
  const frame = useCurrentFrame();

  /* ── part A: departures board (0 → 2) ── */
  const aIn = tw(t, 0, 0.7, 1.4, 0.98, EXPO_OUT);
  const aDrift = tw(t, 0.7, B0, 0, 0.05, (x) => x);
  const aOut = tw(t, B0 - 0.1, B0 + 0.12, 0, 1, EXPO_IN);
  const aRotX = tw(t, 0, 1.2, 28, 12, EXPO_OUT);

  /* ── part B: 3-hour interview (2 → 4) ── */
  const bIn = tw(t, B0 - 0.1, B0 + 0.15, 1, 0, EXPO_OUT);
  const bOut = tw(t, C0 - 0.12, C0, 0, 1, EXPO_IN);
  const counterP = tw(t, B0 + 0.05, B0 + 1.5, 0, 1, EXPO_OUT);
  const secs = Math.round(counterP * (3 * 3600 + 12 * 60 + 47));
  const hh = Math.floor(secs / 3600);
  const mm = Math.floor((secs % 3600) / 60);
  const ss = secs % 60;
  const stamp = `${hh}:${String(mm).padStart(2, '0')}:${String(ss).padStart(2, '0')}`;
  const cardS = sp(t, B0, {damping: 16, stiffness: 140});
  const word1 = sp(t, B0, {damping: 13, stiffness: 260});
  const word2 = sp(t, B0 + 0.5, {damping: 13, stiffness: 260});

  /* ── part C: zero wi-fi (4 → 8) ── */
  const flood = tw(t, 6.6, 7.1, 0, 1, EXPO_OUT);
  const toggleOn = tw(t, 6.5, 6.7, 0, 1, EXPO_OUT);
  const zero = sp(t, 5.5, {damping: 12, stiffness: 300});
  const wifiWord = sp(t, 6.0, {damping: 12, stiffness: 300});
  const toggleIn = sp(t, 6.35, {damping: 14, stiffness: 220});
  const wifiOut = tw(t, 6.3, 6.5, 0, 1, EXPO_IN);
  const offline = sp(t, 7.0, {damping: 14, stiffness: 220});
  const exitZoom = tw(t, 7.62, 8.0, 1, 9, EXPO_IN);
  const shake = pulse(t - 5.5, 0.5, 9) * (t >= 5.5 && t < 6.5 ? 10 : 0);
  const sx = Math.sin(frame * 2.1) * shake;
  const sy = Math.cos(frame * 1.7) * shake;

  const bump = 1 + pulse(t, 1, 8) * 0.012;

  return (
    <AbsoluteFill style={{background: C.ink, overflow: 'hidden'}}>
      {/* ───────── A ───────── */}
      {t < B0 + 0.15 ? (
        <DirBlur id="hookA" y={aOut * 60}>
          <AbsoluteFill
            style={{
              background: `radial-gradient(ellipse at 50% 0%, #1B2140 0%, ${C.ink} 60%)`,
              transform: `translateY(${-aOut * 1400}px)`,
            }}
          >
            {/* dot matrix backing */}
            <AbsoluteFill
              style={{
                backgroundImage: 'radial-gradient(rgba(255,255,255,0.07) 1.5px, transparent 1.5px)',
                backgroundSize: '22px 22px',
              }}
            />
            <AbsoluteFill style={{perspective: 1600, display: 'grid', placeItems: 'center'}}>
              <div
                style={{
                  transform: `scale(${(aIn + aDrift) * bump}) rotateX(${aRotX}deg) rotateZ(${tw(t, 0, 1.2, -4, -1)}deg)`,
                  transformStyle: 'preserve-3d',
                }}
              >
                <Board t={t} />
              </div>
            </AbsoluteFill>
          </AbsoluteFill>
        </DirBlur>
      ) : null}

      {/* ───────── B ───────── */}
      {t >= B0 - 0.1 && t < C0 + 0.05 ? (
        <DirBlur id="hookB" y={Math.abs(bIn) * 50 + bOut * 40}>
          <AbsoluteFill
            style={{
              background: `radial-gradient(ellipse at 50% 100%, #2A1308 0%, ${C.ink} 65%)`,
              transform: `translateY(${bIn * 1400}px) scale(${1 + bOut * 0.6})`,
              opacity: 1 - bOut,
            }}
          >
            <div style={{position: 'absolute', left: 56, top: 120, right: 56}}>
              <div
                style={{
                  fontFamily: serif,
                  fontSize: 120,
                  color: '#FFFFFF',
                  opacity: 0.9,
                  lineHeight: 1,
                  transform: `translateY(${(1 - word1) * 60}px)`,
                  marginBottom: 6,
                }}
              >
                a
                <span
                  style={{
                    fontFamily: display,
                    fontStyle: 'normal',
                    fontWeight: 900,
                    fontSize: 236,
                    letterSpacing: '-0.06em',
                    marginLeft: 26,
                    display: 'inline-block',
                    transform: `scale(${0.6 + word1 * 0.4})`,
                    transformOrigin: '0% 80%',
                  }}
                >
                  3-HOUR
                </span>
              </div>
              <div
                style={{
                  fontFamily: display,
                  fontWeight: 900,
                  fontSize: 168,
                  letterSpacing: '-0.055em',
                  lineHeight: 0.9,
                  color: '#fff',
                  opacity: t >= 2.5 ? 1 : 0,
                  transform: `scale(${1.35 - word2 * 0.35})`,
                  transformOrigin: '0% 50%',
                  filter: `blur(${(1 - word2) * 10}px)`,
                }}
              >
                INTERVIEW.
              </div>
            </div>

            {/* player card */}
            <div
              style={{
                position: 'absolute',
                left: 56,
                top: 640,
                width: 968,
                borderRadius: 30,
                overflow: 'hidden',
                background: C.ink2,
                boxShadow: '0 40px 80px -30px rgba(0,0,0,0.8), inset 0 1px 0 rgba(255,255,255,0.06)',
                transform: `translateY(${(1 - cardS) * 500}px) rotate(${(1 - cardS) * 6}deg)`,
              }}
            >
              <div style={{position: 'relative', height: 545}}>
                <InterviewThumb w={968} h={545} />
                <div style={{position: 'absolute', inset: 0, background: 'linear-gradient(180deg, transparent 50%, rgba(0,0,0,0.65))'}} />
                <div style={{position: 'absolute', left: 32, bottom: 34, fontFamily: sans, fontWeight: 700, fontSize: 34, color: '#fff', letterSpacing: '-0.01em'}}>
                  The 3-hour interview I saved for my flight
                </div>
                <div
                  style={{
                    position: 'absolute',
                    right: 26,
                    top: 26,
                    background: 'rgba(0,0,0,0.78)',
                    borderRadius: 14,
                    padding: '8px 18px',
                    fontFamily: displayMono,
                    fontWeight: 800,
                    fontSize: 56,
                    color: '#fff',
                    fontVariantNumeric: 'tabular-nums',
                  }}
                >
                  {stamp}
                </div>
              </div>
              <div style={{height: 10, background: '#333'}}>
                <div style={{width: `${counterP * 100}%`, height: '100%', background: C.ytRed, boxShadow: `0 0 20px ${C.ytRed}`}} />
              </div>
            </div>
          </AbsoluteFill>
        </DirBlur>
      ) : null}

      {/* ───────── C ───────── */}
      {t >= C0 - 0.05 ? (
        <AbsoluteFill
          style={{
            background: `radial-gradient(ellipse at 50% 30%, #121A33 0%, ${C.ink} 60%)`,
            transform: `translate(${sx}px, ${sy}px) scale(${exitZoom})`,
            transformOrigin: '635px 470px',
          }}
        >
          {/* orange flood from the toggle knob */}
          <div
            style={{
              position: 'absolute',
              left: 540 + 95 - 1800 * flood,
              top: 470 - 1800 * flood,
              width: 3600 * flood,
              height: 3600 * flood,
              borderRadius: '50%',
              background: C.orange,
            }}
          />
          {/* wifi */}
          <div
            style={{
              position: 'absolute',
              left: 540 - 230,
              top: 160,
              transform: `scale(${(1 - wifiOut * 0.6) * tw(t, C0, C0 + 0.3, 0.6, 1, BACK_OUT)})`,
              opacity: 1 - wifiOut,
            }}
          >
            <Wifi t={t} size={460} />
          </div>
          {/* toggle */}
          {t >= 6.3 ? (
            <div
              style={{
                position: 'absolute',
                left: 540 - 220,
                top: 345,
                transform: `scale(${toggleIn})`,
              }}
            >
              <PlaneToggle on={toggleOn} />
            </div>
          ) : null}
          {/* words */}
          <div
            style={{
              position: 'absolute',
              left: 0,
              right: 0,
              top: 690,
              textAlign: 'center',
              fontFamily: display,
              fontWeight: 900,
              fontSize: 250,
              letterSpacing: '-0.06em',
              lineHeight: 0.86,
              color: flood > 0.5 ? C.ink : '#FFFFFF',
            }}
          >
            <div style={{opacity: t >= 5.5 ? 1 : 0, transform: `scale(${1.6 - zero * 0.6})`, filter: `blur(${(1 - zero) * 8}px)`}}>ZERO</div>
            <div style={{opacity: t >= 6 ? 1 : 0, transform: `scale(${1.6 - wifiWord * 0.6})`, filter: `blur(${(1 - wifiWord) * 8}px)`}}>WI-FI.</div>
          </div>
          <div
            style={{
              position: 'absolute',
              left: 0,
              right: 0,
              top: 1218,
              textAlign: 'center',
              fontFamily: mono,
              fontWeight: 700,
              fontSize: 36,
              letterSpacing: '0.14em',
              color: C.ink,
              opacity: offline,
              transform: `translateY(${(1 - offline) * 30}px)`,
            }}
          >
            … AND I NEED IT OFFLINE.
          </div>
        </AbsoluteFill>
      ) : null}

      {/* ───────── sound ───────── */}
      <Sfx name="boom" at={0} volume={0.9} />
      <Sfx name="flaps" at={0} volume={0.55} />
      <Sfx name="blip" at={1.5} volume={0.35} />
      <Sfx name="whoosh" at={B0 - 0.15} volume={0.5} />
      <Sfx name="hit" at={B0} volume={0.8} />
      <Sfx name="ticks" at={B0 + 0.05} volume={0.3} />
      <Sfx name="hit" at={B0 + 0.5} volume={0.7} />
      <Sfx name="whoosh" at={C0 - 0.15} volume={0.45} />
      <Sfx name="blip_down1" at={C0 + 0.125} volume={0.45} />
      <Sfx name="blip_down2" at={C0 + 0.25} volume={0.45} />
      <Sfx name="blip_down3" at={C0 + 0.375} volume={0.45} />
      <Sfx name="hit" at={5.5} volume={0.85} />
      <Sfx name="error" at={5.5} volume={0.3} />
      <Sfx name="hit" at={6} volume={0.8} />
      <Sfx name="toggle" at={6.5} volume={0.7} />
      <Sfx name="boom" at={6.6} volume={0.6} />
      <Sfx name="pop" at={7} volume={0.4} />
      <Sfx name="whoosh_long" at={7.45} volume={0.55} />
    </AbsoluteFill>
  );
};

