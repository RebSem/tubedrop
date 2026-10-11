import React from 'react';
import {AbsoluteFill} from 'remotion';
import {C} from '../config';
import {display, mono, serif} from '../fonts';
import {EXPO_IN, EXPO_OUT, STRONG_IN_OUT, STRONG_OUT, pulse, sp, tw, useBeat} from '../anim';
import {DirBlur, I, MaskLine, Sfx} from '../components/common';

const Label: React.FC<{children: React.ReactNode; color: string; p: number}> = ({children, color, p}) => (
  <MaskLine p={p}>
    <div style={{fontFamily: mono, fontWeight: 700, fontSize: 30, letterSpacing: '0.16em', textTransform: 'uppercase', color}}>{children}</div>
  </MaskLine>
);

/* 360p ✕ → 4K */
const CardQuality: React.FC<{t: number}> = ({t}) => {
  const a = sp(t, 0, {damping: 13, stiffness: 300});
  const strike = tw(t, 0.5, 0.75, 0, 1, EXPO_OUT);
  const b = sp(t, 1.0, {damping: 11, stiffness: 260});
  return (
    <AbsoluteFill style={{background: C.ink}}>
      <div style={{position: 'absolute', left: 64, top: 120}}>
        <Label color="#8A8A92" p={tw(t, 0, 0.35, 0, 1, STRONG_OUT)}>
          YouTube, logged out
        </Label>
        <div
          style={{
            position: 'relative',
            fontFamily: display,
            fontWeight: 900,
            fontSize: 300,
            letterSpacing: '-0.07em',
            lineHeight: 0.95,
            color: strike > 0 ? '#4A4A55' : '#fff',
            transform: `scale(${1.3 - a * 0.3})`,
            transformOrigin: '0% 50%',
            marginTop: 6,
          }}
        >
          360p
          <svg width="640" height="300" style={{position: 'absolute', left: -10, top: 10, overflow: 'visible'}}>
            <line x1="0" y1="190" x2={640 * strike} y2={190 - 120 * strike} stroke={C.red} strokeWidth="26" strokeLinecap="round" />
          </svg>
        </div>
      </div>
      <div style={{position: 'absolute', left: 64, top: 640}}>
        <Label color={C.blueHi} p={tw(t, 0.95, 1.3, 0, 1, STRONG_OUT)}>
          tubedrop · your browser login
        </Label>
        <div
          style={{
            fontFamily: display,
            fontWeight: 900,
            fontSize: 420,
            letterSpacing: '-0.07em',
            lineHeight: 0.9,
            color: C.blueHi,
            opacity: t >= 1 ? 1 : 0,
            transform: `scale(${1.6 - b * 0.6})`,
            transformOrigin: '0% 60%',
            filter: `blur(${(1 - b) * 12}px) drop-shadow(0 0 60px rgba(61,136,255,${0.5 * pulse(t - 1, 1, 4)}))`,
            textShadow: '0 0 80px rgba(0,102,255,0.45)',
          }}
        >
          4K
        </div>
        <div style={{fontFamily: mono, fontSize: 28, color: '#9C9CA6', marginTop: 10, opacity: tw(t, 1.3, 1.6, 0, 1)}}>
          cookies never leave your mac
        </div>
      </div>
    </AbsoluteFill>
  );
};

/* MP4 ⇄ MP3 */
const CardFormat: React.FC<{t: number}> = ({t}) => {
  // highlight hops on every 8th note
  const hop = (x: number) => tw(t, x, x + 0.18, 0, 1, STRONG_IN_OUT);
  const pos = hop(0.5) - hop(1.0) + hop(1.5);
  const inP = sp(t, 0, {damping: 14, stiffness: 240});
  const rowH = 300;
  return (
    <AbsoluteFill style={{background: C.paper}}>
      <div style={{position: 'absolute', left: 64, top: 120}}>
        <Label color={C.muted} p={tw(t, 0, 0.35, 0, 1, STRONG_OUT)}>
          video or audio
        </Label>
      </div>
      <div style={{position: 'absolute', left: 64, right: 64, top: 250, height: rowH * 2 + 20, transform: `translateY(${(1 - inP) * 200}px)`, opacity: inP}}>
        <div
          style={{
            position: 'absolute',
            left: 0,
            right: 0,
            top: pos * (rowH + 20),
            height: rowH,
            borderRadius: 48,
            background: C.blue,
            boxShadow: '0 30px 60px -20px rgba(0,102,255,0.6)',
          }}
        />
        {[
          {tag: 'MP4', icon: <I.video size={110} stroke={2.2} />, sub: 'up to 4K60'},
          {tag: 'MP3', icon: <I.music size={110} stroke={2.2} />, sub: 'with cover art'},
        ].map((r, i) => {
          const on = i === 0 ? pos < 0.5 : pos >= 0.5;
          return (
            <div
              key={r.tag}
              style={{
                position: 'absolute',
                left: 0,
                right: 0,
                top: i * (rowH + 20),
                height: rowH,
                display: 'flex',
                alignItems: 'center',
                padding: '0 56px',
                gap: 44,
                color: on ? '#fff' : C.text,
              }}
            >
              {r.icon}
              <div style={{fontFamily: display, fontWeight: 900, fontSize: 230, letterSpacing: '-0.07em', lineHeight: 1}}>{r.tag}</div>
              <div style={{marginLeft: 'auto', fontFamily: mono, fontSize: 26, fontWeight: 600, opacity: 0.8, textAlign: 'right', width: 160}}>{r.sub}</div>
            </div>
          );
        })}
      </div>
      <div style={{position: 'absolute', left: 64, right: 64, top: 1150, fontFamily: mono, fontSize: 30, color: C.muted, opacity: tw(t, 0.4, 0.8, 0, 1)}}>
        playlists · subtitles · VK Video too
      </div>
    </AbsoluteFill>
  );
};

/* FREE. */
const CardFree: React.FC<{t: number}> = ({t}) => {
  const letters = 'FREE.'.split('');
  return (
    <AbsoluteFill style={{background: C.blue}}>
      <AbsoluteFill
        style={{
          backgroundImage: 'radial-gradient(rgba(255,255,255,0.16) 2px, transparent 2px)',
          backgroundSize: '36px 36px',
          opacity: 0.6,
        }}
      />
      <div style={{position: 'absolute', left: 64, top: 150}}>
        <Label color="rgba(255,255,255,0.75)" p={tw(t, 0, 0.35, 0, 1, STRONG_OUT)}>
          price
        </Label>
      </div>
      <div
        style={{
          position: 'absolute',
          left: 40,
          right: 40,
          top: 330,
          display: 'flex',
          justifyContent: 'center',
          fontFamily: display,
          fontWeight: 900,
          fontSize: 370,
          letterSpacing: '-0.07em',
          lineHeight: 1,
          color: '#fff',
        }}
      >
        {letters.map((ch, i) => {
          const k = sp(t, i * 0.12, {damping: 10, stiffness: 300, mass: 0.6});
          return (
            <span key={i} style={{display: 'inline-block', transform: `translateY(${(1 - k) * 420}px) rotate(${(1 - k) * 18}deg)`, opacity: t >= i * 0.12 ? 1 : 0}}>
              {ch}
            </span>
          );
        })}
      </div>
      <div style={{position: 'absolute', left: 0, right: 0, top: 770, display: 'flex', justifyContent: 'center', gap: 18}}>
        {['no ads', 'no popups', 'no paywall'].map((s, i) => {
          const k = sp(t, 0.75 + i * 0.25, {damping: 12, stiffness: 300});
          return (
            <div
              key={s}
              style={{
                padding: '16px 28px',
                borderRadius: 999,
                background: 'rgba(255,255,255,0.14)',
                border: '2px solid rgba(255,255,255,0.35)',
                fontFamily: mono,
                fontWeight: 700,
                fontSize: 32,
                color: '#fff',
                transform: `scale(${k})`,
                display: 'flex',
                alignItems: 'center',
                gap: 10,
              }}
            >
              <I.x size={26} color="#fff" stroke={3} />
              {s}
            </div>
          );
        })}
      </div>
      <div style={{position: 'absolute', left: 0, right: 0, top: 1000, textAlign: 'center', fontFamily: serif, fontSize: 64, color: 'rgba(255,255,255,0.9)', opacity: tw(t, 1.3, 1.7, 0, 1)}}>
        no account. no catch.
      </div>
    </AbsoluteFill>
  );
};

/* OPEN SOURCE + macOS */
const CardOpen: React.FC<{t: number}> = ({t}) => {
  const l1 = tw(t, 0, 0.35, 0, 1, STRONG_OUT);
  const l2 = tw(t, 0.25, 0.6, 0, 1, STRONG_OUT);
  const chip = sp(t, 0.9, {damping: 12, stiffness: 260});
  return (
    <AbsoluteFill style={{background: C.ink}}>
      <div style={{position: 'absolute', left: 64, top: 140}}>
        <Label color="#8A8A92" p={l1}>
          MIT licensed
        </Label>
      </div>
      <div style={{position: 'absolute', left: 58, top: 230, fontFamily: display, fontWeight: 900, fontSize: 228, letterSpacing: '-0.07em', lineHeight: 0.88, color: '#fff'}}>
        <MaskLine p={l1}>OPEN</MaskLine>
        <MaskLine p={l2}>
          <span>SOURCE</span>
          <span style={{color: C.blueHi}}>.</span>
        </MaskLine>
      </div>
      <div style={{position: 'absolute', left: 64, top: 760, display: 'flex', gap: 18, transform: `translateY(${(1 - chip) * 80}px)`, opacity: chip}}>
        <div style={{display: 'flex', alignItems: 'center', gap: 16, padding: '20px 30px', borderRadius: 999, background: '#fff', color: C.ink, fontFamily: mono, fontWeight: 700, fontSize: 36}}>
          <I.github size={40} color={C.ink} /> on GitHub
        </div>
        <div style={{display: 'flex', alignItems: 'center', gap: 14, padding: '20px 30px', borderRadius: 999, border: '2px solid #3A3A44', color: '#fff', fontFamily: mono, fontWeight: 700, fontSize: 36}}>
          for macOS
        </div>
      </div>
      <div style={{position: 'absolute', left: 64, right: 64, top: 960, fontFamily: mono, fontSize: 28, lineHeight: 1.6, color: '#8A8A92', opacity: tw(t, 1.1, 1.5, 0, 1)}}>
        built on <span style={{color: '#fff'}}>kaifcodec/ytconverter</span>
        <br />+ yt-dlp + ffmpeg. go star them too.
      </div>
    </AbsoluteFill>
  );
};

export const Features: React.FC = () => {
  const t = useBeat();
  const whipIn = tw(t, 0, 0.25, 1, 0, EXPO_OUT);
  const shown = t < 2 ? 0 : t < 4 ? 1 : t < 6 ? 2 : 3;
  const local = t - shown * 2;
  // each card punches in on its downbeat
  const punch = 1 + tw(local, 0, 0.3, 0.06, 0, EXPO_OUT);
  const out = tw(t, 7.75, 8, 0, 1, EXPO_IN);
  return (
    <AbsoluteFill style={{background: C.ink, overflow: 'hidden'}}>
      <DirBlur id="featWhip" x={whipIn * 70 + out * 40}>
        <AbsoluteFill style={{transform: `translateX(${whipIn * 1300}px) scale(${punch}) translateY(${-out * 300}px)`, opacity: 1 - out}}>
          {shown === 0 ? <CardQuality t={local} /> : null}
          {shown === 1 ? <CardFormat t={local} /> : null}
          {shown === 2 ? <CardFree t={local} /> : null}
          {shown === 3 ? <CardOpen t={local} /> : null}
        </AbsoluteFill>
      </DirBlur>
      {/* sound */}
      <Sfx name="hit" at={0} volume={0.85} />
      <Sfx name="swipe" at={0.5} volume={0.6} />
      <Sfx name="hit" at={1} volume={0.8} />
      <Sfx name="hit" at={2} volume={0.85} />
      <Sfx name="tick" at={2.5} volume={0.5} />
      <Sfx name="tick" at={3.0} volume={0.5} />
      <Sfx name="tick" at={3.5} volume={0.5} />
      <Sfx name="hit" at={4} volume={0.9} />
      {[0.75, 1.0, 1.25].map((x) => (
        <Sfx key={x} name="pop" at={4 + x} volume={0.35} />
      ))}
      <Sfx name="hit" at={6} volume={0.85} />
      <Sfx name="pop" at={6.9} volume={0.35} />
      <Sfx name="whoosh_up" at={7.6} volume={0.5} />
    </AbsoluteFill>
  );
};
