import React from 'react';
import {AbsoluteFill} from 'remotion';
import {C} from '../config';
import {display, mono, serif} from '../fonts';
import {EXPO_IN, EXPO_OUT, STRONG_IN_OUT, STRONG_OUT, rand, sp, tw, useBeat} from '../anim';
import {Cursor, I, Logo, MaskLine, Sfx} from '../components/common';

const WORDS = [
  {n: '01', w: 'Install.', at: 0},
  {n: '02', w: 'Paste.', at: 1},
  {n: '03', w: 'Fly.', at: 2},
];

// flight path for the plane (screen coords), cubic bezier
const P0 = [-120, 1180];
const P1 = [380, 1240];
const P2 = [700, 760];
const P3 = [1240, 420];
const bez = (k: number) => {
  const u = 1 - k;
  const x = u * u * u * P0[0] + 3 * u * u * k * P1[0] + 3 * u * k * k * P2[0] + k * k * k * P3[0];
  const y = u * u * u * P0[1] + 3 * u * u * k * P1[1] + 3 * u * k * k * P2[1] + k * k * k * P3[1];
  return [x, y];
};

export const Outro: React.FC = () => {
  const t = useBeat();

  /* part A: Install. Paste. Fly. (0 → 3.4) */
  const aOut = tw(t, 3.0, 3.4, 0, 1, EXPO_IN);
  const fly = tw(t, 2.2, 3.3, 0, 1, STRONG_IN_OUT);
  const [px, py] = bez(fly);
  const [qx, qy] = bez(Math.min(1, fly + 0.01));
  const ang = (Math.atan2(qy - py, qx - px) * 180) / Math.PI;

  // trail as sampled path
  const trail: string[] = [];
  for (let i = 0; i <= 60; i++) {
    const k = (i / 60) * fly;
    const [x, y] = bez(k);
    trail.push(`${i === 0 ? 'M' : 'L'}${x.toFixed(1)} ${y.toFixed(1)}`);
  }

  /* part B: end card (3.2 → 8) */
  const wipe = tw(t, 3.05, 3.5, 0, 1, STRONG_IN_OUT);
  const logoK = sp(t, 3.45, {damping: 9, stiffness: 200, mass: 0.8});
  const logoFall = tw(t, 3.3, 3.55, 0, 1, (x) => x * x);
  const word = (i: number) => sp(t, 3.7 + i * 0.05, {damping: 10, stiffness: 240, mass: 0.6});
  const tag = tw(t, 4.1, 4.5, 0, 1, STRONG_OUT);
  const btn = sp(t, 4.5, {damping: 13, stiffness: 220});
  const cursorK = tw(t, 4.9, 5.4, 0, 1, STRONG_IN_OUT);
  const click = 5.5;
  const press = t >= click ? tw(t, click, click + 0.2, 1, 0) : 0;
  const ripple = t >= click && t < click + 0.5 ? tw(t, click, click + 0.5, 0, 1, (x) => x) : -1;
  const starK = sp(t, click, {damping: 8, stiffness: 260});
  const cursorOut = tw(t, 6.1, 6.5, 0, 1, EXPO_IN);
  const foot = tw(t, 5.0, 5.5, 0, 1, STRONG_OUT);
  const shine = tw(t, 6.2, 7.4, 0, 1, (x) => x);

  return (
    <AbsoluteFill style={{background: C.paper, overflow: 'hidden'}}>
      {/* ───── A ───── */}
      {t < 3.6 ? (
        <AbsoluteFill style={{transform: `translateY(${-aOut * 260}px)`, opacity: 1 - aOut}}>
          <AbsoluteFill style={{background: `radial-gradient(circle at 20% 0%, #FFFFFF 0%, ${C.paper} 45%, #E8E6E0 100%)`}} />
          <div style={{position: 'absolute', left: 64, top: 150}}>
            {WORDS.map((w, i) => {
              const k = sp(t, w.at, {damping: 13, stiffness: 300});
              const isFly = w.w === 'Fly.';
              return (
                <div key={w.n} style={{display: 'flex', alignItems: 'flex-start', gap: 26, height: isFly ? 400 : 270, opacity: t >= w.at ? 1 : 0}}>
                  <div
                    style={{
                      marginTop: isFly ? 70 : 44,
                      fontFamily: mono,
                      fontWeight: 600,
                      fontSize: 26,
                      padding: '4px 10px',
                      borderRadius: 8,
                      background: isFly ? C.blueSoft : 'rgba(15,15,20,0.06)',
                      color: isFly ? C.blue : C.muted,
                    }}
                  >
                    {w.n}
                  </div>
                  <div
                    style={{
                      fontFamily: isFly ? serif : display,
                      fontWeight: isFly ? 500 : 900,
                      fontSize: isFly ? 360 : 250,
                      letterSpacing: isFly ? '-0.04em' : '-0.065em',
                      lineHeight: 1,
                      color: isFly ? C.blue : C.text,
                      transform: `translateX(${(1 - k) * 140}px) scale(${1.15 - k * 0.15})`,
                      transformOrigin: '0% 70%',
                      filter: `blur(${(1 - k) * 8}px)`,
                    }}
                  >
                    {w.w}
                  </div>
                </div>
              );
            })}
          </div>
          {/* plane + dashed trail */}
          <svg width="1080" height="1350" style={{position: 'absolute', inset: 0}}>
            <path d={trail.join(' ')} stroke={C.blue} strokeWidth="9" strokeDasharray="6 22" strokeLinecap="round" fill="none" />
          </svg>
          {fly > 0 && fly < 1 ? (
            <div style={{position: 'absolute', left: px - 90, top: py - 90, transform: `rotate(${ang + 45}deg)`, filter: 'drop-shadow(0 18px 18px rgba(11,11,16,0.25))'}}>
              <I.plane size={180} color={C.ink} />
            </div>
          ) : null}
        </AbsoluteFill>
      ) : null}

      {/* ───── B: end card ───── */}
      {t >= 3.0 ? (
        <AbsoluteFill style={{clipPath: `circle(${wipe * 160}% at 100% 30%)`}}>
          <AbsoluteFill style={{background: `radial-gradient(circle at 20% 0%, #FFFFFF 0%, ${C.paper} 40%, #E8E6E0 100%)`}} />
          <AbsoluteFill
            style={{
              backgroundImage: 'radial-gradient(rgba(15,15,20,0.06) 1.5px, transparent 1.5px)',
              backgroundSize: '28px 28px',
              maskImage: 'radial-gradient(circle at 50% 40%, black 0%, transparent 70%)',
            }}
          />
          {/* logo */}
          <div
            style={{
              position: 'absolute',
              left: 540 - 120,
              top: 170 + (logoFall - 1) * 500,
              transformOrigin: '50% 100%',
              transform: `scale(${1 + (1 - logoK) * 0.25}, ${1 - (1 - logoK) * 0.25})`,
            }}
          >
            <Logo size={240} shine={shine} glow={0.3} />
          </div>
          {/* wordmark */}
          <div
            style={{
              position: 'absolute',
              left: 0,
              right: 0,
              top: 470,
              textAlign: 'center',
              fontFamily: mono,
              fontWeight: 700,
              fontSize: 168,
              letterSpacing: '-0.045em',
              lineHeight: 1,
              color: C.text,
            }}
          >
            {'tubedrop'.split('').map((ch, i) => {
              const k = word(i);
              return (
                <span key={i} style={{display: 'inline-block', opacity: t >= 3.7 + i * 0.05 ? 1 : 0, transform: `translateY(${(1 - k) * -200}px)`}}>
                  {ch}
                </span>
              );
            })}
          </div>
          {/* tagline */}
          <div style={{position: 'absolute', left: 0, right: 0, top: 680, display: 'flex', justifyContent: 'center'}}>
            <MaskLine p={tag}>
              <div style={{fontFamily: display, fontWeight: 700, fontSize: 60, letterSpacing: '-0.035em', color: C.text, textAlign: 'center'}}>
                Free YouTube downloader <span style={{fontFamily: serif, fontWeight: 500, fontStyle: 'italic', color: C.blue}}>for Mac</span>
              </div>
            </MaskLine>
          </div>
          <div style={{position: 'absolute', left: 0, right: 0, top: 770, textAlign: 'center', fontFamily: mono, fontSize: 30, color: C.muted, opacity: tag}}>
            MP4 up to 4K · MP3 · no ads, ever
          </div>
          {/* the button */}
          <div
            style={{
              position: 'absolute',
              left: 90,
              right: 90,
              top: 880,
              height: 140,
              borderRadius: 70,
              background: C.ink,
              display: 'flex',
              alignItems: 'center',
              padding: '0 18px 0 46px',
              gap: 24,
              color: '#fff',
              transform: `translateY(${(1 - btn) * 300}px) scale(${1 - press * 0.04})`,
              boxShadow: `0 ${30 - press * 16}px 60px -20px rgba(11,11,16,0.55), inset 0 1px 0 rgba(255,255,255,0.12)`,
            }}
          >
            <I.github size={58} color="#fff" />
            <div style={{fontFamily: mono, fontWeight: 600, fontSize: 38, letterSpacing: '-0.01em'}}>
              github.com/<span style={{fontWeight: 800}}>RebSem/tubedrop</span>
            </div>
            <div
              style={{
                marginLeft: 'auto',
                height: 104,
                width: 104,
                borderRadius: 52,
                background: t >= click ? C.blue : '#24242C',
                display: 'grid',
                placeItems: 'center',
                transform: `scale(${t >= click ? 0.8 + starK * 0.2 : 1})`,
              }}
            >
              <I.star size={50} color={t >= click ? '#FFE14D' : '#fff'} />
            </div>
          </div>
          {/* star burst */}
          {t >= click && t < click + 1.2
            ? [...Array(12)].map((_, i) => {
                const a = (i / 12) * Math.PI * 2;
                const k = tw(t, click, click + 1.2, 0, 1, EXPO_OUT);
                const r = 70 + k * (120 + rand(i) * 80);
                return (
                  <div
                    key={i}
                    style={{position: 'absolute', left: 938 + Math.cos(a) * r - 12, top: 950 + Math.sin(a) * r - 12, opacity: 1 - k, transform: `rotate(${k * 200}deg) scale(${1 - k * 0.5})`}}
                  >
                    <I.star size={24} color={i % 2 ? C.blue : '#FFB800'} />
                  </div>
                );
              })
            : null}
          {/* cursor */}
          {t >= 4.9 && cursorOut < 1 ? (
            <Cursor
              x={1150 - (1150 - 930) * cursorK + cursorOut * 300}
              y={1400 - (1400 - 960) * cursorK + cursorOut * 300}
              size={64}
              press={press}
              ripple={ripple}
              rippleColor={C.blue}
            />
          ) : null}
          {/* footer */}
          <div style={{position: 'absolute', left: 0, right: 0, top: 1080, textAlign: 'center', opacity: foot, transform: `translateY(${(1 - foot) * 30}px)`}}>
            <div style={{fontFamily: display, fontWeight: 700, fontSize: 40, letterSpacing: '-0.02em', color: C.text}}>
              Link in the post <span style={{color: C.blue}}>·</span> questions welcome
            </div>
            <div style={{marginTop: 46, fontFamily: mono, fontSize: 24, color: C.subtle, letterSpacing: '0.04em'}}>
              built by Mikhail Semenov · rebsem.ru
            </div>
          </div>
        </AbsoluteFill>
      ) : null}

      {/* sound */}
      <Sfx name="hit" at={0} volume={0.85} />
      <Sfx name="hit" at={1} volume={0.85} />
      <Sfx name="boom" at={2} volume={0.7} />
      <Sfx name="swish" at={2.2} volume={0.7} />
      <Sfx name="whoosh_long" at={3.0} volume={0.45} />
      <Sfx name="thump" at={3.55} volume={0.8} />
      {'tubedrop'.split('').map((_, i) => (
        <Sfx key={i} name="pop" at={3.7 + i * 0.05} volume={0.15} />
      ))}
      <Sfx name="whoosh" at={4.45} volume={0.3} />
      <Sfx name="click" at={click} volume={0.8} />
      <Sfx name="sparkle" at={click} volume={0.55} />
      <Sfx name="ding" at={6.2} volume={0.25} />
    </AbsoluteFill>
  );
};

