import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {C} from '../config';
import {display, mono, sans} from '../fonts';
import {BACK_OUT, EXPO_IN, EXPO_OUT, clamp, pulse, rand, sp, tw, useBeat} from '../anim';
import {Cursor, I, Sfx} from '../components/common';

type Pop = {
  at: number;
  x: number;
  y: number;
  w: number;
  rot: number;
  kind:
    | 'notify'
    | 'dl'
    | 'virus'
    | 'prize'
    | 'quality'
    | 'ext'
    | 'adblock'
    | 'captcha'
    | 'failed'
    | 'err';
  label?: string;
};

// x/y are screen coords of the popup's top-left (frame is 1080×1350)
const POPS: Pop[] = [
  {at: 0.75, x: 70, y: 420, w: 560, rot: 0, kind: 'notify'},
  {at: 1.0, x: 300, y: 760, w: 520, rot: -2, kind: 'dl', label: 'DOWNLOAD'},
  {at: 1.5, x: 420, y: 470, w: 600, rot: 3, kind: 'virus'},
  {at: 2.0, x: 90, y: 930, w: 560, rot: -4, kind: 'prize'},
  {at: 2.5, x: 560, y: 1000, w: 430, rot: 5, kind: 'dl', label: 'START DOWNLOAD'},
  {at: 2.75, x: 140, y: 610, w: 600, rot: 1, kind: 'quality'},
  {at: 3.0, x: 470, y: 760, w: 560, rot: -3, kind: 'ext'},
  {at: 3.25, x: 60, y: 1110, w: 470, rot: 2, kind: 'adblock'},
  {at: 3.5, x: 230, y: 380, w: 500, rot: -5, kind: 'dl', label: 'DOWNLOAD (HD)'},
  {at: 3.75, x: 580, y: 610, w: 430, rot: 4, kind: 'captcha'},
  {at: 4.0, x: 250, y: 840, w: 560, rot: 0, kind: 'failed'},
  ...[0, 1, 2, 3, 4, 5].map((i) => ({
    at: 4.25 + i * 0.125,
    x: 110 + i * 70,
    y: 330 + i * 70,
    w: 520,
    rot: 0,
    kind: 'err' as const,
  })),
];

const shadow = '0 30px 60px -20px rgba(0,0,0,0.45), 0 2px 6px rgba(0,0,0,0.12)';

const PopBody: React.FC<{p: Pop}> = ({p}) => {
  switch (p.kind) {
    case 'notify':
      return (
        <div style={{background: '#fff', borderRadius: 18, padding: '24px 28px', boxShadow: shadow, fontFamily: sans}}>
          <div style={{display: 'flex', gap: 16, alignItems: 'center', fontSize: 27, fontWeight: 600, color: '#222'}}>
            <I.bell size={30} color="#555" />
            free-yt-download-4k.biz wants to
          </div>
          <div style={{fontSize: 25, color: '#555', margin: '10px 0 18px 46px'}}>Show notifications</div>
          <div style={{display: 'flex', gap: 12, justifyContent: 'flex-end'}}>
            <div style={{padding: '10px 26px', borderRadius: 999, border: '2px solid #ccc', fontSize: 24, fontWeight: 600, color: '#1a5fd0'}}>Block</div>
            <div style={{padding: '10px 26px', borderRadius: 999, background: '#1a5fd0', fontSize: 24, fontWeight: 600, color: '#fff'}}>Allow</div>
          </div>
        </div>
      );
    case 'dl':
      return (
        <div
          style={{
            background: 'linear-gradient(180deg,#3BE36B,#11A83C)',
            borderRadius: 16,
            padding: '30px 0',
            boxShadow: `${shadow}, inset 0 -6px 0 rgba(0,0,0,0.2), inset 0 3px 0 rgba(255,255,255,0.5)`,
            textAlign: 'center',
            fontFamily: display,
            fontWeight: 900,
            fontSize: 50,
            letterSpacing: '-0.02em',
            color: '#fff',
            textShadow: '0 3px 0 rgba(0,0,0,0.25)',
            position: 'relative',
          }}
        >
          ▼ {p.label}
          <div style={{position: 'absolute', right: 10, top: 8, fontFamily: sans, fontSize: 16, fontWeight: 700, background: '#FFE14D', color: '#333', padding: '2px 7px', borderRadius: 4, textShadow: 'none'}}>Ad</div>
        </div>
      );
    case 'virus':
      return (
        <div style={{background: '#fff', borderRadius: 14, overflow: 'hidden', boxShadow: shadow, fontFamily: sans}}>
          <div style={{background: '#E3122B', color: '#fff', padding: '16px 24px', fontSize: 30, fontWeight: 800, display: 'flex', gap: 14, alignItems: 'center'}}>
            <I.alert size={34} color="#fff" /> WARNING!
          </div>
          <div style={{padding: '20px 24px', fontSize: 30, fontWeight: 700, color: '#111', lineHeight: 1.2}}>
            Your Mac is infected with <span style={{color: '#E3122B'}}>(3) viruses!</span>
          </div>
          <div style={{margin: '0 24px 22px', padding: '14px 0', textAlign: 'center', background: '#E3122B', color: '#fff', borderRadius: 10, fontWeight: 800, fontSize: 28}}>CLEAN NOW</div>
        </div>
      );
    case 'prize':
      return (
        <div
          style={{
            background: 'repeating-linear-gradient(45deg,#FFE14D 0 26px,#FFD000 26px 52px)',
            borderRadius: 18,
            padding: '26px 28px',
            boxShadow: shadow,
            fontFamily: sans,
            border: '5px solid #fff',
          }}
        >
          <div style={{display: 'flex', alignItems: 'center', gap: 14, fontSize: 34, fontWeight: 900, color: '#C2185B'}}>
            <I.gift size={40} color="#C2185B" /> CONGRATULATIONS!!
          </div>
          <div style={{fontSize: 28, fontWeight: 700, color: '#222', marginTop: 8}}>You won an iPhone 17 Pro</div>
          <div style={{marginTop: 14, display: 'inline-block', padding: '10px 24px', background: '#C2185B', color: '#fff', fontWeight: 800, borderRadius: 999, fontSize: 24}}>CLAIM NOW →</div>
        </div>
      );
    case 'quality':
      return (
        <div style={{background: '#fff', borderRadius: 16, padding: '22px 26px', boxShadow: shadow, fontFamily: sans}}>
          <div style={{fontSize: 22, color: '#777', fontWeight: 600}}>Quality</div>
          <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 8, padding: '12px 18px', border: '2px solid #ddd', borderRadius: 10, fontSize: 32, fontWeight: 800, color: '#111'}}>
            360p <span style={{fontSize: 22, color: '#999'}}>▾</span>
          </div>
          <div style={{marginTop: 12, fontSize: 23, color: '#B00020', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8}}>
            <I.lock size={22} color="#B00020" /> 720p+ only in PRO · $9.99/mo
          </div>
        </div>
      );
    case 'ext':
      return (
        <div style={{background: '#fff', borderRadius: 16, padding: '22px 26px', boxShadow: shadow, fontFamily: sans, display: 'flex', gap: 18, alignItems: 'center'}}>
          <div style={{width: 74, height: 74, borderRadius: 16, background: '#7E57C2', display: 'grid', placeItems: 'center'}}>
            <I.puzzle size={42} color="#fff" />
          </div>
          <div>
            <div style={{fontSize: 27, fontWeight: 800, color: '#111'}}>Install “VideoSaver Plus”</div>
            <div style={{fontSize: 22, color: '#666', marginTop: 4}}>Required to continue download</div>
            <div style={{marginTop: 10, display: 'inline-block', padding: '8px 18px', background: '#1a5fd0', color: '#fff', borderRadius: 8, fontWeight: 700, fontSize: 21}}>Add to browser</div>
          </div>
        </div>
      );
    case 'adblock':
      return (
        <div style={{background: '#2B2B33', borderRadius: 16, padding: '24px 26px', boxShadow: shadow, fontFamily: sans, color: '#fff'}}>
          <div style={{fontSize: 30, fontWeight: 800}}>AdBlock detected :(</div>
          <div style={{fontSize: 22, color: '#bbb', marginTop: 6}}>Please disable it to download</div>
        </div>
      );
    case 'captcha':
      return (
        <div style={{background: '#F9F9F9', borderRadius: 8, padding: '22px 22px', boxShadow: shadow, fontFamily: sans, display: 'flex', gap: 18, alignItems: 'center', border: '2px solid #ddd'}}>
          <div style={{width: 48, height: 48, border: '3px solid #bbb', borderRadius: 4, background: '#fff'}} />
          <div style={{fontSize: 30, fontWeight: 600, color: '#222'}}>I’m not a robot</div>
        </div>
      );
    case 'failed':
      return (
        <div style={{background: '#ECECEC', borderRadius: 18, padding: '26px 28px', boxShadow: shadow, fontFamily: sans, display: 'flex', gap: 20, alignItems: 'center'}}>
          <div style={{width: 70, height: 70, borderRadius: 35, background: '#E3122B', display: 'grid', placeItems: 'center', flexShrink: 0}}>
            <I.x size={40} color="#fff" stroke={3} />
          </div>
          <div>
            <div style={{fontSize: 32, fontWeight: 800, color: '#111'}}>Download failed</div>
            <div style={{fontSize: 23, color: '#666', marginTop: 4}}>Server busy. Try again in 30 min.</div>
          </div>
        </div>
      );
    case 'err':
      return (
        <div style={{background: '#fff', borderRadius: 12, overflow: 'hidden', boxShadow: shadow, fontFamily: sans, border: '2px solid #bbb'}}>
          <div style={{background: 'linear-gradient(180deg,#E9E9EE,#D7D7DE)', padding: '10px 16px', display: 'flex', gap: 8, alignItems: 'center'}}>
            {['#FF5F57', '#FEBC2E', '#28C840'].map((c) => (
              <div key={c} style={{width: 16, height: 16, borderRadius: 8, background: c}} />
            ))}
            <div style={{marginLeft: 12, fontSize: 20, fontWeight: 700, color: '#555'}}>Error</div>
          </div>
          <div style={{padding: '22px 22px', fontSize: 27, fontWeight: 700, color: '#111', display: 'flex', alignItems: 'center', gap: 14}}>
            <I.alert size={34} color="#E3122B" /> Video unavailable. Try PRO.
          </div>
        </div>
      );
  }
};

const Stamp: React.FC<{t: number; at: number; x: number; y: number; rot: number}> = ({t, at, x, y, rot}) => {
  if (t < at - 0.12) return null;
  const k = tw(t, at - 0.12, at, 0, 1, EXPO_IN);
  const s = 2.6 - k * 1.6;
  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        transform: `rotate(${rot}deg) scale(${s})`,
        opacity: clamp(k * 2),
        zIndex: 40,
      }}
    >
      <svg width="560" height="230" viewBox="0 0 560 230" style={{overflow: 'visible'}}>
        <defs>
          <filter id={`rough${at}`}>
            <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed={at * 10} result="n" />
            <feDisplacementMap in="SourceGraphic" in2="n" scale="7" />
            <feComponentTransfer>
              <feFuncA type="discrete" tableValues="0 1 1 1 1 1 0.85 1" />
            </feComponentTransfer>
          </filter>
        </defs>
        <g filter={`url(#rough${at})`}>
          <rect x="10" y="10" width="540" height="210" rx="26" fill="none" stroke={C.red} strokeWidth="14" />
          <rect x="30" y="30" width="500" height="170" rx="14" fill="none" stroke={C.red} strokeWidth="4" />
          <text x="280" y="170" textAnchor="middle" fontFamily={display} fontWeight={900} fontSize="168" letterSpacing="-6" fill={C.red}>
            SCAM.
          </text>
        </g>
      </svg>
    </div>
  );
};

export const Scam: React.FC = () => {
  const t = useBeat();
  const frame = useCurrentFrame();

  // camera shake builds with the chaos, kicks on every stamp
  const chaos = tw(t, 1, 4.6, 0, 1, (x) => x);
  const stampKick = [5, 5.5, 6].reduce((a, s) => a + (t >= s ? pulse(t - s, 10, 18) : 0), 0);
  const amp = chaos * 7 + stampKick * 26;
  const shx = Math.sin(frame * 2.3) * amp;
  const shy = Math.cos(frame * 1.9) * amp;
  const zoom = tw(t, 0, 5, 1.0, 1.08, (x) => x);

  // everything falls at 6.5
  const fall = (i: number) => {
    const t0 = 6.45 + rand(i * 7.7) * 0.3;
    const dt = Math.max(0, t - t0);
    return {y: 0.5 * 6400 * dt * dt, r: dt * (rand(i) * 2 - 1) * 140};
  };

  // glitch at the end
  const glitch = t > 7.3 ? tw(t, 7.3, 8, 0, 1, (x) => x) : 0;

  // the cursor: frantic clicks on fake buttons
  const path: [number, number, number][] = [
    [0.4, 1150, 1400],
    [0.95, 560, 860],
    [1.25, 560, 860],
    [2.4, 760, 1080],
    [2.75, 760, 1080],
    [3.35, 480, 460],
    [3.6, 480, 460],
    [3.7, 640, 680],
    [3.9, 660, 690],
    [4.6, 520, 930],
    [5.2, 540, 980],
  ];
  let cx = path[0][1];
  let cy = path[0][2];
  for (let i = 0; i < path.length - 1; i++) {
    const [ta, xa, ya] = path[i];
    const [tb, xb, yb] = path[i + 1];
    if (t >= ta) {
      const k = tw(t, ta, tb, 0, 1, EXPO_OUT);
      cx = xa + (xb - xa) * k + Math.sin(t * 40) * chaos * 6;
      cy = ya + (yb - ya) * k + Math.cos(t * 37) * chaos * 6;
    }
  }
  const clicks = [1.25, 2.75, 3.6, 3.9];
  const lastClick = clicks.filter((c) => t >= c).pop();
  const press = lastClick !== undefined ? tw(t, lastClick, lastClick + 0.15, 1, 0) : 0;
  const ripple = lastClick !== undefined ? tw(t, lastClick, lastClick + 0.4, 0, 1, (x) => x) : -1;

  const caption = sp(t, 0, {damping: 16, stiffness: 200});

  return (
    <AbsoluteFill style={{background: C.ink, overflow: 'hidden'}}>
      <AbsoluteFill style={{transform: `translate(${shx}px, ${shy}px) scale(${zoom})`}}>
        {/* fake browser */}
        <div
          style={{
            position: 'absolute',
            left: 36,
            top: 250,
            width: 1008,
            height: 1060,
            borderRadius: 26,
            overflow: 'hidden',
            background: '#F3F3F5',
            boxShadow: '0 40px 100px -30px rgba(0,0,0,0.9)',
            transform: `translateY(${fall(99).y * 0.7}px) rotate(${fall(99).r * 0.15}deg)`,
          }}
        >
          <div style={{height: 76, background: '#E4E4E9', display: 'flex', alignItems: 'center', padding: '0 24px', gap: 12}}>
            {['#FF5F57', '#FEBC2E', '#28C840'].map((c) => (
              <div key={c} style={{width: 18, height: 18, borderRadius: 9, background: c}} />
            ))}
            <div
              style={{
                marginLeft: 18,
                flex: 1,
                height: 46,
                borderRadius: 12,
                background: '#fff',
                display: 'flex',
                alignItems: 'center',
                padding: '0 18px',
                gap: 10,
                fontFamily: sans,
                fontSize: 22,
                color: '#444',
              }}
            >
              <I.alert size={22} color="#D93025" />
              <span style={{color: '#D93025', fontWeight: 700}}>Not secure</span>
              <span style={{color: '#999'}}>|</span>
              free-yt-download-4k.biz/convert?hd=1&amp;ref=ad
            </div>
          </div>
          <div
            style={{
              height: 170,
              background: 'linear-gradient(90deg,#FF2D55,#FF9500,#FFCC00)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontFamily: display,
              fontWeight: 900,
              fontSize: 64,
              color: '#fff',
              letterSpacing: '-0.03em',
              textShadow: '0 4px 0 rgba(0,0,0,0.2)',
            }}
          >
            YT→MP4 4K FREE!!! ★★★★★
          </div>
          <div style={{padding: '40px 50px'}}>
            <div style={{height: 84, borderRadius: 12, border: '3px solid #ccc', background: '#fff', display: 'flex', alignItems: 'center', padding: '0 24px', fontFamily: sans, fontSize: 28, color: '#aaa'}}>
              Paste YouTube link here…
            </div>
            <div style={{display: 'flex', gap: 20, marginTop: 30}}>
              {[0, 1, 2].map((i) => (
                <div key={i} style={{flex: 1, height: 220, borderRadius: 14, background: `repeating-linear-gradient(135deg,#e6e6ea 0 14px,#efeff2 14px 28px)`, display: 'grid', placeItems: 'center', fontFamily: sans, fontWeight: 800, color: '#bbb', fontSize: 26}}>
                  AD
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* popups */}
        {POPS.map((p, i) => {
          if (t < p.at) return null;
          const k = sp(t, p.at, {damping: 11, stiffness: 320, mass: 0.6});
          const fl = fall(i);
          return (
            <div
              key={i}
              style={{
                position: 'absolute',
                left: p.x,
                top: p.y,
                width: p.w,
                transform: `translateY(${fl.y}px) rotate(${p.rot + fl.r}deg) scale(${k})`,
                transformOrigin: '50% 50%',
                zIndex: 10 + i,
              }}
            >
              <PopBody p={p} />
            </div>
          );
        })}

        {/* stamps */}
        <div style={{position: 'absolute', inset: 0, transform: `translateY(${fall(77).y}px) rotate(${fall(77).r * 0.3}deg)`, zIndex: 60}}>
          <Stamp t={t} at={5} x={60} y={430} rot={-12} />
          <Stamp t={t} at={5.5} x={470} y={730} rot={9} />
          <Stamp t={t} at={6} x={140} y={1010} rot={-5} />
        </div>

        {t < 6.6 ? (
          <Cursor x={cx} y={cy} size={52} press={press} ripple={ripple} rippleColor="#11A83C" />
        ) : null}
      </AbsoluteFill>

      {/* caption bar — stays put while the page shakes */}
      <div
        style={{
          position: 'absolute',
          left: 56,
          right: 56,
          top: 70,
          fontFamily: display,
          fontWeight: 800,
          fontSize: 74,
          letterSpacing: '-0.04em',
          lineHeight: 1.0,
          color: '#fff',
          transform: `translateY(${(1 - caption) * -40}px)`,
          opacity: caption,
          zIndex: 80,
        }}
      >
        So I tried every
        <br />
        <span style={{color: C.yellow}}>“free” downloader.</span>
      </div>

      {/* glitch slices */}
      {glitch > 0 ? (
        <AbsoluteFill style={{zIndex: 90, pointerEvents: 'none'}}>
          {[...Array(14)].map((_, i) => {
            const on = rand(i * 3 + Math.floor(frame / 2)) < 0.35 + glitch * 0.5;
            if (!on) return null;
            const y = rand(i * 11 + Math.floor(frame / 2)) * 1350;
            const h = 10 + rand(i * 5 + frame) * 80;
            return (
              <div
                key={i}
                style={{
                  position: 'absolute',
                  left: 0,
                  right: 0,
                  top: y,
                  height: h,
                  background: i % 3 === 0 ? C.blue : i % 3 === 1 ? C.red : '#fff',
                  mixBlendMode: i % 3 === 2 ? 'difference' : 'screen',
                  opacity: 0.85,
                  transform: `translateX(${(rand(i + frame) - 0.5) * 200}px)`,
                }}
              />
            );
          })}
        </AbsoluteFill>
      ) : null}
      {t > 7.85 ? <AbsoluteFill style={{background: '#000', zIndex: 95}} /> : null}

      {/* sound */}
      <Sfx name="whoosh" at={0} volume={0.4} />
      {POPS.map((p, i) => (
        <Sfx key={i} name={p.kind === 'dl' ? 'pop' : `error${(i % 3) + 1}`} at={p.at} volume={p.kind === 'err' ? 0.22 : 0.32} />
      ))}
      {clicks.map((c) => (
        <Sfx key={c} name="click" at={c} volume={0.6} />
      ))}
      <Sfx name="stamp" at={5} volume={1} />
      <Sfx name="stamp" at={5.5} volume={1} />
      <Sfx name="stamp" at={6} volume={1} />
      <Sfx name="fall" at={6.45} volume={0.6} />
      <Sfx name="glitch" at={7.3} volume={0.55} />
    </AbsoluteFill>
  );
};

