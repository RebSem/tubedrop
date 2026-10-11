import React from 'react';
import {AbsoluteFill} from 'remotion';
import {C} from '../config';
import {display, displayMono, mono, serif} from '../fonts';
import {EXPO_IN, EXPO_OUT, STRONG_IN_OUT, STRONG_OUT, sp, tw, useBeat} from '../anim';
import {MaskLine, Sfx} from '../components/common';
import {CODE_LINES} from '../code-lines';

const PROMPT = 'build me a mac app: paste a youtube link → get the file. full HD. mp3 too.';

export const Vibe: React.FC = () => {
  const t = useBeat();

  const year = sp(t, 0, {damping: 13, stiffness: 280});
  const l2 = tw(t, 1.0, 1.4, 0, 1, STRONG_OUT);
  const l3 = sp(t, 1.5, {damping: 12, stiffness: 220});
  const underline = tw(t, 1.7, 2.3, 0, 1, EXPO_OUT);
  const textOut = tw(t, 2.8, 3.15, 0, 1, EXPO_IN);

  const ringIn = sp(t, 3.0, {damping: 15, stiffness: 160});
  const prog = tw(t, 3.35, 4.85, 0, 1, STRONG_IN_OUT);
  const secs = Math.round(prog * 600);
  const mmss = `${String(Math.floor(secs / 60)).padStart(2, '0')}:${String(secs % 60).padStart(2, '0')}`;
  const done = t >= 4.85;
  const works = sp(t, 4.85, {damping: 11, stiffness: 300});
  const collapse = tw(t, 5.3, 5.5, 0, 1, EXPO_IN);
  const launch = tw(t, 5.48, 5.72, 0, 1, EXPO_IN);

  const typed = Math.floor(tw(t, 3.05, 4.1, 0, PROMPT.length, (x) => x));
  const promptIn = tw(t, 2.95, 3.3, 0, 1, EXPO_OUT);

  // code rain speeds up toward the drop
  const rainOn = tw(t, 2.6, 3.4, 0, 1, (x) => x) * (1 - collapse);
  const scroll = Math.pow(Math.max(0, t - 2.6), 2.2) * 260;
  const glow = tw(t, 2, 5.5, 0.15, 1, (x) => x) * (1 - launch);

  const R = 300;
  const circ = 2 * Math.PI * R;
  const ringR = R * (1 - collapse * 0.92);

  return (
    <AbsoluteFill style={{background: C.ink, overflow: 'hidden'}}>
      <AbsoluteFill
        style={{
          background: `radial-gradient(circle at 50% 50%, rgba(0,102,255,${0.35 * glow}) 0%, rgba(0,102,255,0) 55%)`,
        }}
      />

      {/* code rain: real lines from tubedrop's source */}
      <AbsoluteFill style={{opacity: rainOn * 0.55, overflow: 'hidden'}}>
        <div
          style={{
            position: 'absolute',
            left: 48,
            top: 1350 - (scroll % (CODE_LINES.length * 40)),
            fontFamily: mono,
            fontSize: 25,
            lineHeight: '40px',
            whiteSpace: 'pre',
            color: '#3D88FF',
          }}
        >
          {[...CODE_LINES, ...CODE_LINES, ...CODE_LINES].map((l, i) => (
            <div key={i} style={{opacity: 0.25 + ((i * 37) % 10) / 20}}>
              {l}
            </div>
          ))}
        </div>
        <AbsoluteFill style={{background: `linear-gradient(180deg, ${C.ink} 0%, transparent 25%, transparent 70%, ${C.ink} 100%)`}} />
      </AbsoluteFill>

      {/* statement */}
      {t < 3.2 ? (
        <AbsoluteFill
          style={{
            transform: `translateY(${-textOut * 220}px) scale(${1 - textOut * 0.25})`,
            opacity: 1 - textOut,
            filter: `blur(${textOut * 12}px)`,
          }}
        >
          <div
            style={{
              position: 'absolute',
              left: 0,
              right: 0,
              top: 230,
              textAlign: 'center',
              fontFamily: display,
              fontWeight: 900,
              fontSize: 168,
              letterSpacing: '-0.06em',
              color: '#fff',
              transform: `scale(${1.5 - year * 0.5})`,
              filter: `blur(${(1 - year) * 10}px)`,
            }}
          >
            It’s 2026.
          </div>
          <div style={{position: 'absolute', left: 0, right: 0, top: 520, display: 'flex', justifyContent: 'center'}}>
            <MaskLine p={l2}>
              <div style={{fontFamily: serif, fontSize: 112, color: 'rgba(255,255,255,0.82)', lineHeight: 1.05}}>You can just</div>
            </MaskLine>
          </div>
          <div
            style={{
              position: 'absolute',
              left: 0,
              right: 0,
              top: 660,
              textAlign: 'center',
              fontFamily: serif,
              fontWeight: 500,
              fontSize: 250,
              letterSpacing: '-0.035em',
              lineHeight: 1,
              color: C.blueHi,
              opacity: t >= 1.5 ? 1 : 0,
              transform: `translateY(${(1 - l3) * 80}px) scale(${0.8 + l3 * 0.2})`,
            }}
          >
            build it.
            <svg width="760" height="60" viewBox="0 0 760 60" style={{display: 'block', margin: '-10px auto 0'}}>
              <path
                d="M10 40 C 180 10, 420 10, 750 30"
                stroke={C.blueHi}
                strokeWidth="12"
                fill="none"
                strokeLinecap="round"
                strokeDasharray="800"
                strokeDashoffset={800 * (1 - underline)}
              />
            </svg>
          </div>
        </AbsoluteFill>
      ) : null}

      {/* the prompt */}
      {t >= 2.95 ? (
        <div
          style={{
            position: 'absolute',
            left: 60,
            right: 60,
            top: 110,
            padding: '26px 30px',
            borderRadius: 26,
            background: 'rgba(31,31,40,0.92)',
            border: '1.5px solid rgba(255,255,255,0.1)',
            boxShadow: '0 30px 80px -30px rgba(0,0,0,0.9)',
            fontFamily: mono,
            fontSize: 32,
            lineHeight: 1.45,
            color: '#F2F2F4',
            opacity: promptIn * (1 - collapse),
            transform: `translateY(${(1 - promptIn) * -40 - launch * 300}px)`,
            display: 'flex',
            gap: 18,
          }}
        >
          <span style={{color: C.blueHi, fontWeight: 700}}>›</span>
          <span>
            {PROMPT.slice(0, typed)}
            {typed < PROMPT.length ? <span style={{color: C.blueHi}}>▍</span> : null}
          </span>
        </div>
      ) : null}

      {/* stopwatch */}
      {t >= 3.0 ? (
        <div
          style={{
            position: 'absolute',
            left: 540 - R - 40,
            top: 760 - R - 40,
            width: 2 * R + 80,
            height: 2 * R + 80,
            transform: `translateY(${-launch * 1300}px) scale(${ringIn})`,
          }}
        >
          <svg width={2 * R + 80} height={2 * R + 80} style={{overflow: 'visible'}}>
            <g transform={`translate(${R + 40} ${R + 40})`}>
              {[...Array(60)].map((_, i) => {
                const a = (i / 60) * Math.PI * 2;
                const lit = i / 60 <= prog;
                const long = i % 5 === 0;
                return (
                  <line
                    key={i}
                    x1={Math.sin(a) * (ringR + 34)}
                    y1={-Math.cos(a) * (ringR + 34)}
                    x2={Math.sin(a) * (ringR + (long ? 58 : 46))}
                    y2={-Math.cos(a) * (ringR + (long ? 58 : 46))}
                    stroke={lit ? C.blueHi : '#2A2A34'}
                    strokeWidth={long ? 5 : 3}
                    strokeLinecap="round"
                    opacity={1 - collapse}
                  />
                );
              })}
              <circle r={ringR} fill={collapse > 0 ? C.blue : 'none'} fillOpacity={collapse} stroke="#1F1F28" strokeWidth={26} />
              <circle
                r={ringR}
                fill="none"
                stroke={done ? '#fff' : C.blue}
                strokeWidth={26}
                strokeLinecap="round"
                strokeDasharray={circ}
                strokeDashoffset={circ * (1 - prog)}
                transform="rotate(-90)"
                style={{filter: `drop-shadow(0 0 ${18 + prog * 30}px rgba(0,102,255,0.8))`}}
              />
            </g>
          </svg>
          <div
            style={{
              position: 'absolute',
              inset: 0,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              opacity: 1 - collapse,
            }}
          >
            <div style={{fontFamily: mono, fontWeight: 700, fontSize: 28, letterSpacing: '0.22em', color: C.blueHi}}>VIBE-CODING</div>
            <div
              style={{
                fontFamily: displayMono,
                fontWeight: 800,
                fontSize: 176,
                letterSpacing: '-0.04em',
                color: '#fff',
                fontVariantNumeric: 'tabular-nums',
                lineHeight: 1.05,
                transform: `scale(${done ? 1 + tw(t, 4.85, 5.05, 0.12, 0, EXPO_OUT) : 1})`,
              }}
            >
              {mmss}
            </div>
            {done ? (
              <div
                style={{
                  marginTop: 6,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 10,
                  padding: '8px 22px',
                  borderRadius: 999,
                  background: '#16A34A',
                  fontFamily: mono,
                  fontWeight: 700,
                  fontSize: 34,
                  color: '#fff',
                  transform: `scale(${works})`,
                }}
              >
                ✓ it works
              </div>
            ) : (
              <div style={{fontFamily: mono, fontWeight: 600, fontSize: 28, letterSpacing: '0.2em', color: 'rgba(255,255,255,0.45)', marginTop: 14}}>ELAPSED</div>
            )}
          </div>
        </div>
      ) : null}

      <Sfx name="hit" at={0} volume={0.8} />
      <Sfx name="whoosh" at={0.95} volume={0.35} />
      <Sfx name="hit" at={1.5} volume={0.75} />
      <Sfx name="whoosh" at={2.8} volume={0.4} />
      <Sfx name="type_long" at={3.05} volume={0.3} />
      <Sfx name="ticks" at={3.35} volume={0.32} />
      <Sfx name="riser" at={2} volume={0.6} />
      <Sfx name="ding" at={4.85} volume={0.45} />
      <Sfx name="whoosh_up" at={5.35} volume={0.6} />
    </AbsoluteFill>
  );
};
